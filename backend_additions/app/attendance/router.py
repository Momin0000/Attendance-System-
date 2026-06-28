"""
Phase 3 - Attendance Router
Add to main.py: from app.attendance.router import router as attendance_router
                app.include_router(attendance_router)
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime
import json

from app.database.session import get_db
from app.models.models import Student, AttendanceRecord, QRCode
from app.core.security import get_current_user, get_operator_or_above, get_admin_or_above

router = APIRouter(prefix="/attendance", tags=["Attendance"])


class QRScanRequest(BaseModel):
    qr_data: str


class ManualAttendanceRequest(BaseModel):
    student_id_code: str
    attendance_date: date
    status: str = "present"
    notes: Optional[str] = None


class AttendanceResponse(BaseModel):
    id: int
    student_db_id: int
    student_id_code: str
    campus_id: int
    batch_id: int
    attendance_date: date
    check_in_time: Optional[datetime]
    status: str
    notes: Optional[str]

    class Config:
        from_attributes = True


def _get_student_by_code(db: Session, code: str) -> Student:
    s = db.query(Student).filter(
        Student.student_id == code,
        Student.is_deleted == False,
        Student.is_active == True,
    ).first()
    if not s:
        raise HTTPException(status_code=404, detail=f"Student not found: {code}")
    return s


def _duplicate_check(db: Session, student_db_id: int, attendance_date: date):
    existing = db.query(AttendanceRecord).filter(
        AttendanceRecord.student_db_id == student_db_id,
        AttendanceRecord.attendance_date == attendance_date,
    ).first()
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"Attendance already marked for this student on {attendance_date}"
        )


@router.post("/scan", response_model=AttendanceResponse)
async def scan_qr(
    data: QRScanRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # Parse QR payload
    try:
        payload = json.loads(data.qr_data)
        student_code = payload.get("student_id")
        if not student_code:
            raise ValueError
    except Exception:
        # Fallback: treat raw string as student_id
        student_code = data.qr_data.strip()

    student = _get_student_by_code(db, student_code)
    today = date.today()
    _duplicate_check(db, student.id, today)

    record = AttendanceRecord(
        student_db_id=student.id,
        student_id_code=student.student_id,
        campus_id=student.campus_id,
        batch_id=student.batch_id,
        attendance_date=today,
        check_in_time=datetime.utcnow(),
        status="present",
        scan_method="qr",
        marked_by=current_user.id,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.post("/manual", response_model=AttendanceResponse)
async def manual_attendance(
    data: ManualAttendanceRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_operator_or_above),
):
    student = _get_student_by_code(db, data.student_id_code)
    _duplicate_check(db, student.id, data.attendance_date)

    record = AttendanceRecord(
        student_db_id=student.id,
        student_id_code=student.student_id,
        campus_id=student.campus_id,
        batch_id=student.batch_id,
        attendance_date=data.attendance_date,
        check_in_time=datetime.utcnow(),
        status=data.status,
        scan_method="manual",
        notes=data.notes,
        marked_by=current_user.id,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/daily", response_model=List[AttendanceResponse])
async def daily_attendance(
    attendance_date: Optional[date] = Query(None),
    batch_id: Optional[int] = Query(None),
    campus_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    target = attendance_date or date.today()
    q = db.query(AttendanceRecord).filter(AttendanceRecord.attendance_date == target)
    if batch_id:
        q = q.filter(AttendanceRecord.batch_id == batch_id)
    if campus_id:
        q = q.filter(AttendanceRecord.campus_id == campus_id)
    return q.order_by(AttendanceRecord.check_in_time.desc()).all()


@router.get("/student/{student_db_id}/history", response_model=List[AttendanceResponse])
async def student_history(
    student_db_id: int,
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    q = db.query(AttendanceRecord).filter(AttendanceRecord.student_db_id == student_db_id)
    if from_date:
        q = q.filter(AttendanceRecord.attendance_date >= from_date)
    if to_date:
        q = q.filter(AttendanceRecord.attendance_date <= to_date)
    return q.order_by(AttendanceRecord.attendance_date.desc()).all()


@router.get("/student/{student_db_id}/summary")
async def student_summary(
    student_db_id: int,
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    student = db.query(Student).filter(Student.id == student_db_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    q = db.query(AttendanceRecord).filter(AttendanceRecord.student_db_id == student_db_id)
    if from_date:
        q = q.filter(AttendanceRecord.attendance_date >= from_date)
    if to_date:
        q = q.filter(AttendanceRecord.attendance_date <= to_date)
    records = q.all()

    total = len(records)
    present = sum(1 for r in records if r.status == "present")
    absent = sum(1 for r in records if r.status == "absent")
    late = sum(1 for r in records if r.status == "late")

    return {
        "student_id": student.id,
        "student_name": student.full_name,
        "student_code": student.student_id,
        "total_classes": total,
        "present": present,
        "absent": absent,
        "late": late,
        "percentage": round(present / total * 100, 2) if total else 0.0,
    }


@router.delete("/{record_id}", status_code=204)
async def delete_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_admin_or_above),
):
    record = db.query(AttendanceRecord).filter(AttendanceRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    db.delete(record)
    db.commit()
