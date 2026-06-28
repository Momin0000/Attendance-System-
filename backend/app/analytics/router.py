"""
Phase 3 - Analytics Router
Add to main.py: from app.analytics.router import router as analytics_router
                app.include_router(analytics_router)
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import date, timedelta

from app.database.session import get_db
from app.models.models import Student, Attendance, Campus, Batch, Course
from app.core.security import get_current_user, get_operator_or_above

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/dashboard")
async def dashboard(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    total_students = db.query(func.count(Student.id)).filter(Student.is_deleted == False).scalar()
    active_students = db.query(func.count(Student.id)).filter(
        Student.is_deleted == False, Student.is_active == True
    ).scalar()
    total_campuses = db.query(func.count(Campus.id)).filter(Campus.is_deleted == False).scalar()
    total_batches = db.query(func.count(Batch.id)).filter(Batch.is_deleted == False).scalar()
    total_courses = db.query(func.count(Course.id)).filter(Course.is_deleted == False).scalar()

    today = date.today()
    today_records = db.query(Attendance).filter(Attendance.attendance_date == today).all()
    today_present = sum(1 for r in today_records if r.status == "present")
    today_pct = round(today_present / active_students * 100, 2) if active_students else 0.0

    weekly_trend = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        recs = db.query(Attendance).filter(Attendance.attendance_date == day).all()
        present = sum(1 for r in recs if r.status == "present")
        weekly_trend.append({
            "date": str(day),
            "present": present,
            "total": len(recs),
            "percentage": round(present / len(recs) * 100, 2) if recs else 0.0,
        })

    campuses = db.query(Campus).filter(Campus.is_deleted == False).all()
    campus_stats = []
    for c in campuses:
        c_total = db.query(func.count(Student.id)).filter(
            Student.campus_id == c.id, Student.is_deleted == False
        ).scalar()
        c_active = db.query(func.count(Student.id)).filter(
            Student.campus_id == c.id, Student.is_deleted == False, Student.is_active == True
        ).scalar()
        c_batches = db.query(func.count(Batch.id)).filter(
            Batch.campus_id == c.id, Batch.is_deleted == False
        ).scalar()
        c_recs = db.query(Attendance).filter(Attendance.campus_id == c.id).all()
        c_present = sum(1 for r in c_recs if r.status == "present")
        c_pct = round(c_present / len(c_recs) * 100, 2) if c_recs else 0.0
        campus_stats.append({
            "campus_id": c.id,
            "campus_name": c.name,
            "total_students": c_total,
            "active_students": c_active,
            "total_batches": c_batches,
            "avg_attendance_percentage": c_pct,
        })

    return {
        "total_students": total_students,
        "active_students": active_students,
        "total_campuses": total_campuses,
        "total_batches": total_batches,
        "total_courses": total_courses,
        "today_attendance_percentage": today_pct,
        "weekly_attendance_trend": weekly_trend,
        "campus_wise_stats": campus_stats,
    }


@router.get("/batch/{batch_id}")
async def batch_analytics(
    batch_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    batch = db.query(Batch).filter(Batch.id == batch_id, Batch.is_deleted == False).first()
    if not batch:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Batch not found")

    campus = db.query(Campus).filter(Campus.id == batch.campus_id).first()
    students_count = db.query(func.count(Student.id)).filter(
        Student.batch_id == batch_id, Student.is_deleted == False
    ).scalar()

    records = db.query(Attendance).filter(Attendance.batch_id == batch_id).all()
    present = sum(1 for r in records if r.status == "present")
    pct = round(present / len(records) * 100, 2) if records else 0.0

    today = date.today()
    trend = []
    for i in range(29, -1, -1):
        day = today - timedelta(days=i)
        day_recs = [r for r in records if r.attendance_date == day]
        day_present = sum(1 for r in day_recs if r.status == "present")
        trend.append({"date": str(day), "present": day_present, "total": len(day_recs)})

    return {
        "batch_id": batch.id,
        "batch_name": batch.name,
        "campus_name": campus.name if campus else "",
        "total_students": students_count,
        "avg_attendance_percentage": pct,
        "attendance_trend": trend,
    }


@router.get("/low-attendance")
async def low_attendance(
    threshold: float = Query(75.0, ge=0, le=100),
    campus_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_operator_or_above),
):
    q = db.query(Student).filter(Student.is_deleted == False, Student.is_active == True)
    if campus_id:
        q = q.filter(Student.campus_id == campus_id)
    students = q.all()

    result = []
    for s in students:
        recs = db.query(Attendance).filter(Attendance.student_db_id == s.id).all()
        if not recs:
            continue
        present = sum(1 for r in recs if r.status == "present")
        pct = round(present / len(recs) * 100, 2)
        if pct < threshold:
            result.append({
                "student_id": s.id,
                "student_code": s.student_id,
                "name": s.full_name,
                "email": s.email,
                "total_classes": len(recs),
                "present": present,
                "percentage": pct,
            })

    return sorted(result, key=lambda x: x["percentage"])
