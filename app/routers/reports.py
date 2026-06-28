from uuid import UUID
from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, require_role
from app.services import reports_service

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/attendance/excel")
def attendance_excel(
    batch_id: Optional[UUID] = Query(None),
    campus_id: Optional[UUID] = Query(None),
    course_id: Optional[UUID] = Query(None),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["admin", "instructor"])),
):
    path = reports_service.export_attendance_excel(db, batch_id, campus_id, course_id, from_date, to_date)
    return FileResponse(
        path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename="attendance_report.xlsx"
    )


@router.get("/attendance/csv")
def attendance_csv(
    batch_id: Optional[UUID] = Query(None),
    campus_id: Optional[UUID] = Query(None),
    course_id: Optional[UUID] = Query(None),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["admin", "instructor"])),
):
    path = reports_service.export_attendance_csv(db, batch_id, campus_id, course_id, from_date, to_date)
    return FileResponse(path, media_type="text/csv", filename="attendance_report.csv")


@router.get("/attendance/pdf")
def attendance_pdf(
    batch_id: Optional[UUID] = Query(None),
    campus_id: Optional[UUID] = Query(None),
    course_id: Optional[UUID] = Query(None),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["admin", "instructor"])),
):
    path = reports_service.export_attendance_pdf(db, batch_id, campus_id, course_id, from_date, to_date)
    return FileResponse(path, media_type="application/pdf", filename="attendance_report.pdf")


@router.get("/students/excel")
def students_excel(
    campus_id: Optional[UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["admin", "instructor"])),
):
    path = reports_service.export_students_excel(db, campus_id)
    return FileResponse(
        path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename="students_report.xlsx"
    )
