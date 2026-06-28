import json
from uuid import UUID
from datetime import date, datetime
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from fastapi import HTTPException

from app.models.student import Student
from app.models.attendance import AttendanceRecord
from app.schemas.attendance import AttendanceManualCreate


def scan_qr_and_mark(db: Session, qr_token: str, marked_by: Optional[UUID] = None) -> AttendanceRecord:
    """
    Parse QR token → find student → duplicate check → mark present.
    """
    try:
        payload = json.loads(qr_token)
        student_db_id = payload.get("uid")
        token_type = payload.get("type")
    except (json.JSONDecodeError, KeyError):
        raise HTTPException(status_code=400, detail="Invalid QR token format")

    if token_type != "attendance":
        raise HTTPException(status_code=400, detail="QR code is not an attendance token")

    student = db.query(Student).filter(Student.id == student_db_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found for this QR code")

    if not student.is_active:
        raise HTTPException(status_code=403, detail="Student account is inactive")

    today = date.today()

    # Duplicate check: already marked today?
    existing = db.query(AttendanceRecord).filter(
        and_(
            AttendanceRecord.student_id == student.id,
            AttendanceRecord.attendance_date == today
        )
    ).first()

    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"Attendance already marked for {student.student_id} on {today}"
        )

    record = AttendanceRecord(
        student_id=student.id,
        batch_id=student.batch_id,
        course_id=student.course_id,
        campus_id=student.campus_id,
        attendance_date=today,
        check_in_time=datetime.utcnow(),
        status="present",
        scan_method="qr",
        qr_token_used=qr_token[:200],
        marked_by=marked_by,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def mark_attendance_manual(
    db: Session,
    data: AttendanceManualCreate,
    marked_by: Optional[UUID] = None
) -> AttendanceRecord:
    student = db.query(Student).filter(Student.id == data.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    existing = db.query(AttendanceRecord).filter(
        and_(
            AttendanceRecord.student_id == data.student_id,
            AttendanceRecord.attendance_date == data.attendance_date
        )
    ).first()
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"Attendance already recorded for this student on {data.attendance_date}"
        )

    record = AttendanceRecord(
        student_id=student.id,
        batch_id=student.batch_id,
        course_id=student.course_id,
        campus_id=student.campus_id,
        attendance_date=data.attendance_date,
        check_in_time=datetime.utcnow(),
        status=data.status,
        scan_method="manual",
        notes=data.notes,
        marked_by=marked_by,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_attendance_by_date(
    db: Session,
    attendance_date: date,
    batch_id: Optional[UUID] = None,
    course_id: Optional[UUID] = None,
    campus_id: Optional[UUID] = None,
):
    query = db.query(AttendanceRecord).filter(
        AttendanceRecord.attendance_date == attendance_date
    )
    if batch_id:
        query = query.filter(AttendanceRecord.batch_id == batch_id)
    if course_id:
        query = query.filter(AttendanceRecord.course_id == course_id)
    if campus_id:
        query = query.filter(AttendanceRecord.campus_id == campus_id)
    return query.all()


def get_student_attendance_history(
    db: Session,
    student_id: UUID,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
):
    query = db.query(AttendanceRecord).filter(
        AttendanceRecord.student_id == student_id
    ).order_by(AttendanceRecord.attendance_date.desc())

    if from_date:
        query = query.filter(AttendanceRecord.attendance_date >= from_date)
    if to_date:
        query = query.filter(AttendanceRecord.attendance_date <= to_date)

    return query.all()


def get_student_attendance_summary(db: Session, student_id: UUID, from_date: Optional[date] = None, to_date: Optional[date] = None):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    records = get_student_attendance_history(db, student_id, from_date, to_date)

    total = len(records)
    present = sum(1 for r in records if r.status == "present")
    absent = sum(1 for r in records if r.status == "absent")
    late = sum(1 for r in records if r.status == "late")
    percentage = round((present / total * 100), 2) if total > 0 else 0.0

    return {
        "student_id": student.id,
        "student_name": f"{student.first_name} {student.last_name}",
        "student_code": student.student_id,
        "total_classes": total,
        "present": present,
        "absent": absent,
        "late": late,
        "percentage": percentage,
    }


def delete_attendance_record(db: Session, record_id: UUID):
    record = db.query(AttendanceRecord).filter(AttendanceRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    db.delete(record)
    db.commit()
