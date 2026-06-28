from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, require_role
from app.services import analytics_service

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/dashboard")
def dashboard(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return analytics_service.get_dashboard_overview(db)


@router.get("/batch/{batch_id}")
def batch_analytics(
    batch_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = analytics_service.get_batch_analytics(db, batch_id)
    if not result:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Batch not found")
    return result


@router.get("/low-attendance")
def low_attendance(
    threshold: float = Query(75.0, ge=0, le=100),
    campus_id: Optional[UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["admin", "instructor"])),
):
    return analytics_service.get_low_attendance_students(db, threshold, campus_id)
