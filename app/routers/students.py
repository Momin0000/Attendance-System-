import os
from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, require_role
from app.schemas.student import StudentCreate, StudentUpdate, StudentResponse, StudentListResponse
from app.services import student_service
from app.models.campus import Campus

router = APIRouter(prefix="/students", tags=["Students"])


@router.post("/", response_model=StudentResponse, status_code=201)
def create_student(
    data: StudentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["admin", "instructor"])),
):
    campus = db.query(Campus).filter(Campus.id == data.campus_id).first()
    if not campus:
        raise HTTPException(status_code=404, detail="Campus not found")
    campus_code = campus.code if hasattr(campus, "code") else campus.name[:3].upper()
    return student_service.create_student(db, data, campus_code)


@router.get("/", response_model=StudentListResponse)
def list_students(
    campus_id: Optional[UUID] = Query(None),
    batch_id: Optional[UUID] = Query(None),
    course_id: Optional[UUID] = Query(None),
    is_active: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    total, students = student_service.list_students(
        db, campus_id, batch_id, course_id, is_active, search, page, page_size
    )
    return {"total": total, "page": page, "page_size": page_size, "students": students}


@router.get("/{student_db_id}", response_model=StudentResponse)
def get_student(
    student_db_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return student_service.get_student(db, student_db_id)


@router.get("/by-student-id/{student_id}", response_model=StudentResponse)
def get_by_student_id(
    student_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return student_service.get_student_by_student_id(db, student_id)


@router.put("/{student_db_id}", response_model=StudentResponse)
def update_student(
    student_db_id: UUID,
    data: StudentUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["admin", "instructor"])),
):
    return student_service.update_student(db, student_db_id, data)


@router.delete("/{student_db_id}", status_code=204)
def delete_student(
    student_db_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["admin"])),
):
    student_service.delete_student(db, student_db_id)


@router.post("/{student_db_id}/photo", response_model=StudentResponse)
def upload_photo(
    student_db_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["admin", "instructor"])),
):
    return student_service.upload_student_photo(db, student_db_id, file)


@router.get("/{student_db_id}/photo")
def get_photo(
    student_db_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    student = student_service.get_student(db, student_db_id)
    if not student.photo_path or not os.path.exists(student.photo_path):
        raise HTTPException(status_code=404, detail="Photo not found")
    return FileResponse(student.photo_path)


@router.post("/{student_db_id}/regenerate-qr", response_model=StudentResponse)
def regenerate_qr(
    student_db_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["admin", "instructor"])),
):
    return student_service.regenerate_qr(db, student_db_id)


@router.get("/{student_db_id}/qr")
def get_qr_code(
    student_db_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    student = student_service.get_student(db, student_db_id)
    if not student.qr_code_path or not os.path.exists(student.qr_code_path):
        raise HTTPException(status_code=404, detail="QR code not found")
    return FileResponse(student.qr_code_path, media_type="image/png")


@router.post("/{student_db_id}/generate-id-card")
def generate_id_card(
    student_db_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["admin", "instructor"])),
):
    path = student_service.generate_id_card(db, student_db_id)
    return {"message": "ID card generated", "path": path}


@router.get("/{student_db_id}/id-card")
def download_id_card(
    student_db_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    student = student_service.get_student(db, student_db_id)
    if not student.id_card_path or not os.path.exists(student.id_card_path):
        raise HTTPException(status_code=404, detail="ID card not generated yet. Call /generate-id-card first.")
    return FileResponse(
        student.id_card_path,
        media_type="application/pdf",
        filename=f"id_card_{student.student_id}.pdf"
    )
