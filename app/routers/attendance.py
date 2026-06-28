from uuid import UUID
from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, require_role
from app.schemas.attendance import (
    QRScanRequest, AttendanceManualCreate, AttendanceResponse,
    AttendanceSummary, DailyAttendanceReport
)
from app.services import attendance_service

router = APIRouter(prefix="/attendance", tags=["Attendance"])


@router.post("/scan-qr", response_model=AttendanceResponse)
def scan_qr(
    data: QRScanRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return attendance_service.scan_qr_and_mark(db, data.qr_token, marked_by=current_user.id)


@router.post("/manual", response_model=AttendanceResponse)
def mark_manual(
    data: AttendanceManualCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["admin", "instructor"])),
):
    return attendance_service.mark_attendance_manual(db, data, marked_by=current_user.id)


@router.get("/daily", response_model=list[AttendanceResponse])
def daily_attendance(
    attendance_date: date = Query(default=None),
    batch_id: Optional[UUID] = Query(None),
    course_id: Optional[UUID] = Query(None),
    campus_id: Optional[UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not attendance_date:
        attendance_date = date.today()
    return attendance_service.get_attendance_by_date(db, attendance_date, batch_id, course_id, campus_id)


@router.get("/student/{student_id}/history", response_model=list[AttendanceResponse])
def student_history(
    student_id: UUID,
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return attendance_service.get_student_attendance_history(db, student_id, from_date, to_date)


@router.get("/student/{student_id}/summary")
def student_summary(
    student_id: UUID,
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return attendance_service.get_student_attendance_summary(db, student_id, from_date, to_date)


@router.delete("/{record_id}", status_code=204)
def delete_record(
    record_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["admin"])),
):
    attendance_service.delete_attendance_record(db, record_id)
