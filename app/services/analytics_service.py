from datetime import date, timedelta
from uuid import UUID
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.models.student import Student
from app.models.attendance import AttendanceRecord


def get_dashboard_overview(db: Session):
    from app.models.campus import Campus
    from app.models.batch import Batch
    from app.models.course import Course

    total_students = db.query(func.count(Student.id)).scalar()
    active_students = db.query(func.count(Student.id)).filter(Student.is_active == True).scalar()
    total_campuses = db.query(func.count(Campus.id)).scalar()
    total_batches = db.query(func.count(Batch.id)).scalar()
    total_courses = db.query(func.count(Course.id)).scalar()

    today = date.today()
    today_records = db.query(AttendanceRecord).filter(
        AttendanceRecord.attendance_date == today
    ).all()
    today_present = sum(1 for r in today_records if r.status == "present")
    today_pct = round((today_present / active_students * 100), 2) if active_students > 0 else 0.0

    # Weekly trend (last 7 days)
    weekly_trend = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_records = db.query(AttendanceRecord).filter(
            AttendanceRecord.attendance_date == day
        ).all()
        present = sum(1 for r in day_records if r.status == "present")
        weekly_trend.append({
            "date": str(day),
            "present": present,
            "total": len(day_records),
            "percentage": round((present / len(day_records) * 100), 2) if day_records else 0.0
        })

    campuses = db.query(Campus).all()
    campus_stats = []
    for campus in campuses:
        c_students = db.query(func.count(Student.id)).filter(Student.campus_id == campus.id).scalar()
        c_active = db.query(func.count(Student.id)).filter(
            Student.campus_id == campus.id, Student.is_active == True
        ).scalar()
        c_batches = db.query(func.count(Batch.id)).filter(Batch.campus_id == campus.id).scalar()
        c_records = db.query(AttendanceRecord).filter(
            AttendanceRecord.campus_id == campus.id
        ).all()
        c_present = sum(1 for r in c_records if r.status == "present")
        c_pct = round((c_present / len(c_records) * 100), 2) if c_records else 0.0

        campus_stats.append({
            "campus_id": str(campus.id),
            "campus_name": campus.name,
            "total_students": c_students,
            "active_students": c_active,
            "total_batches": c_batches,
            "total_courses": 0,
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


def get_batch_analytics(db: Session, batch_id: UUID):
    from app.models.batch import Batch

    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        return None

    students = db.query(Student).filter(Student.batch_id == batch_id).all()
    total = len(students)

    records = db.query(AttendanceRecord).filter(
        AttendanceRecord.batch_id == batch_id
    ).all()

    present = sum(1 for r in records if r.status == "present")
    pct = round((present / len(records) * 100), 2) if records else 0.0

    today = date.today()
    trend = []
    for i in range(29, -1, -1):
        day = today - timedelta(days=i)
        day_recs = [r for r in records if r.attendance_date == day]
        day_present = sum(1 for r in day_recs if r.status == "present")
        trend.append({
            "date": str(day),
            "present": day_present,
            "total": len(day_recs)
        })

    return {
        "batch_id": str(batch.id),
        "batch_name": batch.name,
        "campus_name": batch.campus.name if batch.campus else "",
        "total_students": total,
        "avg_attendance_percentage": pct,
        "attendance_trend": trend,
    }


def get_low_attendance_students(db: Session, threshold: float = 75.0, campus_id: Optional[UUID] = None):
    query = db.query(Student).filter(Student.is_active == True)
    if campus_id:
        query = query.filter(Student.campus_id == campus_id)

    students = query.all()
    result = []

    for student in students:
        records = db.query(AttendanceRecord).filter(
            AttendanceRecord.student_id == student.id
        ).all()
        if not records:
            continue
        present = sum(1 for r in records if r.status == "present")
        pct = round((present / len(records) * 100), 2)
        if pct < threshold:
            result.append({
                "student_id": student.student_id,
                "name": f"{student.first_name} {student.last_name}",
                "email": student.email,
                "total_classes": len(records),
                "present": present,
                "percentage": pct
            })

    return sorted(result, key=lambda x: x["percentage"])
