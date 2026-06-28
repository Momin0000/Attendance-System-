"""
Phase 3 - Students Router
Plugs into Phase 1 backend. Matches Phase 1 pattern exactly.
Add to main.py: from app.students.router import router as students_router
                app.include_router(students_router)
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date
import os
from pathlib import Path

from app.database.session import get_db
from app.models.models import Student, Campus, QRCode, IDCard
from app.core.security import get_current_user, get_operator_or_above, get_admin_or_above
from app.core.config import settings
from app.qr.service import generate_qr_code
from app.idcards.service import generate_id_card_pdf
from PIL import Image

router = APIRouter(prefix="/students", tags=["Students"])


class StudentCreate(BaseModel):
    full_name: str
    father_name: Optional[str] = None
    cnic: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    gender: Optional[str] = None
    date_of_birth: Optional[date] = None
    address: Optional[str] = None
    campus_id: int
    course_id: int
    batch_id: int
    enrollment_date: Optional[date] = None


class StudentUpdate(BaseModel):
    full_name: Optional[str] = None
    father_name: Optional[str] = None
    cnic: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    gender: Optional[str] = None
    date_of_birth: Optional[date] = None
    address: Optional[str] = None
    course_id: Optional[int] = None
    batch_id: Optional[int] = None
    is_active: Optional[bool] = None


class StudentResponse(BaseModel):
    id: int
    student_id: str
    full_name: str
    father_name: Optional[str]
    cnic: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    gender: Optional[str]
    date_of_birth: Optional[date]
    address: Optional[str]
    photo_path: Optional[str]
    campus_id: int
    course_id: int
    batch_id: int
    enrollment_date: date
    is_active: bool

    class Config:
        from_attributes = True


class PaginatedStudents(BaseModel):
    items: List[StudentResponse]
    total: int
    page: int
    page_size: int


def _generate_student_id(db: Session, campus_code: str) -> str:
    prefix = f"BQ-{campus_code.upper()}"
    last = (
        db.query(Student)
        .filter(Student.student_id.like(f"{prefix}-%"))
        .order_by(Student.student_id.desc())
        .first()
    )
    num = int(last.student_id.split("-")[-1]) + 1 if last else 1
    return f"{prefix}-{str(num).zfill(6)}"


@router.post("/", response_model=StudentResponse, status_code=201)
async def create_student(
    data: StudentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_operator_or_above),
):
    campus = db.query(Campus).filter(Campus.id == data.campus_id, Campus.is_deleted == False).first()
    if not campus:
        raise HTTPException(status_code=404, detail="Campus not found")

    student_id = _generate_student_id(db, campus.code)
    enrollment = data.enrollment_date or date.today()

    student = Student(
        student_id=student_id,
        enrollment_date=enrollment,
        **{k: v for k, v in data.model_dump().items() if k != "enrollment_date"},
    )
    db.add(student)
    db.flush()

    # Generate QR code immediately
    qr_path = generate_qr_code(student_id)
    qr = QRCode(student_id_ref=student.id, student_id_code=student_id, qr_image_path=qr_path)
    db.add(qr)
    db.commit()
    db.refresh(student)
    return student


@router.get("/", response_model=PaginatedStudents)
async def list_students(
    campus_id: Optional[int] = Query(None),
    batch_id: Optional[int] = Query(None),
    course_id: Optional[int] = Query(None),
    is_active: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    q = db.query(Student).filter(Student.is_deleted == False)
    if campus_id: q = q.filter(Student.campus_id == campus_id)
    if batch_id: q = q.filter(Student.batch_id == batch_id)
    if course_id: q = q.filter(Student.course_id == course_id)
    if is_active is not None: q = q.filter(Student.is_active == is_active)
    if search:
        q = q.filter(or_(
            Student.full_name.ilike(f"%{search}%"),
            Student.student_id.ilike(f"%{search}%"),
            Student.email.ilike(f"%{search}%"),
            Student.cnic.ilike(f"%{search}%"),
        ))
    total = q.count()
    items = q.order_by(Student.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.get("/by-code/{student_id}", response_model=StudentResponse)
async def get_by_code(
    student_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    s = db.query(Student).filter(Student.student_id == student_id, Student.is_deleted == False).first()
    if not s:
        raise HTTPException(status_code=404, detail="Student not found")
    return s


@router.get("/{student_id}", response_model=StudentResponse)
async def get_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    s = db.query(Student).filter(Student.id == student_id, Student.is_deleted == False).first()
    if not s:
        raise HTTPException(status_code=404, detail="Student not found")
    return s


@router.put("/{student_id}", response_model=StudentResponse)
async def update_student(
    student_id: int,
    data: StudentUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_operator_or_above),
):
    s = db.query(Student).filter(Student.id == student_id, Student.is_deleted == False).first()
    if not s:
        raise HTTPException(status_code=404, detail="Student not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(s, k, v)
    db.commit()
    db.refresh(s)
    return s


@router.delete("/{student_id}")
async def delete_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_admin_or_above),
):
    s = db.query(Student).filter(Student.id == student_id, Student.is_deleted == False).first()
    if not s:
        raise HTTPException(status_code=404, detail="Student not found")
    s.is_deleted = True
    db.commit()
    return {"message": "Student deleted"}


@router.post("/{student_id}/photo", response_model=StudentResponse)
async def upload_photo(
    student_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_operator_or_above),
):
    s = db.query(Student).filter(Student.id == student_id, Student.is_deleted == False).first()
    if not s:
        raise HTTPException(status_code=404, detail="Student not found")
    if file.content_type not in {"image/jpeg", "image/png", "image/jpg"}:
        raise HTTPException(status_code=400, detail="Only JPEG/PNG allowed")

    photos_dir = Path(settings.STORAGE_PATH) / "photos"
    photos_dir.mkdir(parents=True, exist_ok=True)
    ext = file.filename.rsplit(".", 1)[-1]
    filename = f"{s.student_id}.{ext}"
    path = photos_dir / filename
    contents = await file.read()
    with open(path, "wb") as f:
        f.write(contents)
    img = Image.open(path)
    img.thumbnail((800, 800))
    img.save(path)
    s.photo_path = f"photos/{filename}"
    db.commit()
    db.refresh(s)
    return s


@router.get("/{student_id}/qr")
async def get_qr(
    student_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    s = db.query(Student).filter(Student.id == student_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Student not found")
    qr = db.query(QRCode).filter(QRCode.student_id_ref == student_id, QRCode.is_active == True).first()
    if not qr:
        raise HTTPException(status_code=404, detail="QR code not found")
    path = Path(settings.STORAGE_PATH) / qr.qr_image_path
    if not path.exists():
        raise HTTPException(status_code=404, detail="QR file missing")
    return FileResponse(str(path), media_type="image/png")


@router.post("/{student_id}/id-card")
async def generate_id_card(
    student_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_operator_or_above),
):
    s = db.query(Student).filter(Student.id == student_id, Student.is_deleted == False).first()
    if not s:
        raise HTTPException(status_code=404, detail="Student not found")

    from app.models.models import Course, Batch
    course = db.query(Course).filter(Course.id == s.course_id).first()
    batch = db.query(Batch).filter(Batch.id == s.batch_id).first()
    campus = db.query(Campus).filter(Campus.id == s.campus_id).first()
    qr = db.query(QRCode).filter(QRCode.student_id_ref == s.id, QRCode.is_active == True).first()

    student_data = {
        "student_id": s.student_id,
        "full_name": s.full_name,
        "course": course.name if course else "",
        "batch": batch.name if batch else "",
        "campus": campus.name if campus else "",
        "phone": s.phone or "",
        "photo_path": s.photo_path,
        "qr_path": qr.qr_image_path if qr else None,
    }
    pdf_path = generate_id_card_pdf(student_data)
    card = IDCard(student_id_ref=s.id, pdf_path=pdf_path)
    db.add(card)
    db.commit()
    return {"message": "ID card generated", "path": pdf_path}


@router.get("/{student_id}/id-card/download")
async def download_id_card(
    student_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    s = db.query(Student).filter(Student.id == student_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Student not found")
    card = db.query(IDCard).filter(IDCard.student_id_ref == student_id).order_by(IDCard.generated_at.desc()).first()
    if not card:
        raise HTTPException(status_code=404, detail="ID card not generated yet")
    path = Path(settings.STORAGE_PATH) / card.pdf_path
    if not path.exists():
        raise HTTPException(status_code=404, detail="ID card file missing")
    return FileResponse(str(path), media_type="application/pdf", filename=f"{s.student_id}_id_card.pdf")
