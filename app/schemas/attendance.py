from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
from uuid import UUID


class QRScanRequest(BaseModel):
    qr_token: str


class AttendanceManualCreate(BaseModel):
    student_id: UUID
    attendance_date: date
    status: str = "present"
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class AttendanceResponse(BaseModel):
    id: UUID
    student_id: UUID
    batch_id: UUID
    course_id: UUID
    campus_id: UUID
    attendance_date: date
    check_in_time: Optional[datetime] = None
    status: str
    scan_method: str
    notes: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AttendanceSummary(BaseModel):
    student_id: UUID
    student_name: str
    student_code: str
    total_classes: int
    present: int
    absent: int
    late: int
    percentage: float


class DailyAttendanceReport(BaseModel):
    date: date
    batch_id: UUID
    course_id: UUID
    total_students: int
    present: int
    absent: int
    percentage: float
    records: list[AttendanceResponse]
