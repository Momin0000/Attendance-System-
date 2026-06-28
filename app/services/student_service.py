import os
import qrcode
import io
import json
from uuid import UUID
from typing import Optional
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from fastapi import HTTPException, UploadFile
from PIL import Image

from app.models.student import Student
from app.models.attendance import AttendanceRecord
from app.schemas.student import StudentCreate, StudentUpdate
from app.services.id_card_service import generate_student_id_card


UPLOAD_DIR = "uploads/photos"
QR_DIR = "uploads/qr_codes"
ID_CARD_DIR = "uploads/id_cards"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(QR_DIR, exist_ok=True)
os.makedirs(ID_CARD_DIR, exist_ok=True)


def _generate_student_id(db: Session, campus_code: str) -> str:
    """Generate sequential student ID like BQ-KHI-000001"""
    prefix = f"BQ-{campus_code.upper()}"
    last = (
        db.query(Student)
        .filter(Student.student_id.like(f"{prefix}-%"))
        .order_by(Student.student_id.desc())
        .first()
    )
    if last:
        last_num = int(last.student_id.split("-")[-1])
        new_num = last_num + 1
    else:
        new_num = 1
    return f"{prefix}-{str(new_num).zfill(6)}"


def _generate_qr_code(student_id: str, student_db_id: str) -> str:
    """Generate QR code PNG for student and return file path"""
    payload = json.dumps({
        "student_id": student_id,
        "uid": student_db_id,
        "type": "attendance"
    })
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(payload)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    path = os.path.join(QR_DIR, f"{student_db_id}.png")
    img.save(path)
    return path


def get_student(db: Session, student_db_id: UUID) -> Student:
    student = db.query(Student).filter(Student.id == student_db_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


def get_student_by_student_id(db: Session, student_id: str) -> Student:
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


def list_students(
    db: Session,
    campus_id: Optional[UUID] = None,
    batch_id: Optional[UUID] = None,
    course_id: Optional[UUID] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
):
    query = db.query(Student)

    if campus_id:
        query = query.filter(Student.campus_id == campus_id)
    if batch_id:
        query = query.filter(Student.batch_id == batch_id)
    if course_id:
        query = query.filter(Student.course_id == course_id)
    if is_active is not None:
        query = query.filter(Student.is_active == is_active)
    if search:
        query = query.filter(
            (Student.first_name.ilike(f"%{search}%"))
            | (Student.last_name.ilike(f"%{search}%"))
            | (Student.email.ilike(f"%{search}%"))
            | (Student.student_id.ilike(f"%{search}%"))
        )

    total = query.count()
    students = query.offset((page - 1) * page_size).limit(page_size).all()
    return total, students


def create_student(db: Session, data: StudentCreate, campus_code: str) -> Student:
    # Check email duplicate
    if db.query(Student).filter(Student.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    if data.cnic and db.query(Student).filter(Student.cnic == data.cnic).first():
        raise HTTPException(status_code=400, detail="CNIC already registered")

    student_id = _generate_student_id(db, campus_code)

    student = Student(
        student_id=student_id,
        **data.model_dump()
    )
    db.add(student)
    db.flush()  # get the UUID before commit

    # Generate QR code
    qr_path = _generate_qr_code(student_id, str(student.id))
    student.qr_code_path = qr_path

    db.commit()
    db.refresh(student)
    return student


def update_student(db: Session, student_db_id: UUID, data: StudentUpdate) -> Student:
    student = get_student(db, student_db_id)
    update_data = data.model_dump(exclude_unset=True)

    if "email" in update_data:
        existing = db.query(Student).filter(
            Student.email == update_data["email"],
            Student.id != student_db_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already in use")

    for key, val in update_data.items():
        setattr(student, key, val)

    db.commit()
    db.refresh(student)
    return student


def delete_student(db: Session, student_db_id: UUID):
    student = get_student(db, student_db_id)
    db.delete(student)
    db.commit()


def upload_student_photo(db: Session, student_db_id: UUID, file: UploadFile) -> Student:
    student = get_student(db, student_db_id)

    allowed = {"image/jpeg", "image/png", "image/jpg"}
    if file.content_type not in allowed:
        raise HTTPException(status_code=400, detail="Only JPEG/PNG images allowed")

    ext = file.filename.rsplit(".", 1)[-1]
    filename = f"{student_db_id}.{ext}"
    path = os.path.join(UPLOAD_DIR, filename)

    contents = file.file.read()
    with open(path, "wb") as f:
        f.write(contents)

    # Resize to max 800x800
    img = Image.open(path)
    img.thumbnail((800, 800))
    img.save(path)

    student.photo_path = path
    db.commit()
    db.refresh(student)
    return student


def regenerate_qr(db: Session, student_db_id: UUID) -> Student:
    student = get_student(db, student_db_id)
    qr_path = _generate_qr_code(student.student_id, str(student.id))
    student.qr_code_path = qr_path
    db.commit()
    db.refresh(student)
    return student


def generate_id_card(db: Session, student_db_id: UUID) -> str:
    student = get_student(db, student_db_id)
    path = generate_student_id_card(student, ID_CARD_DIR)
    student.id_card_path = path
    db.commit()
    return path
