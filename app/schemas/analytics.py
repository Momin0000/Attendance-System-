from pydantic import BaseModel
from typing import Optional
from datetime import date
from uuid import UUID


class CampusAnalytics(BaseModel):
    campus_id: UUID
    campus_name: str
    total_students: int
    active_students: int
    total_batches: int
    total_courses: int
    avg_attendance_percentage: float


class BatchAnalytics(BaseModel):
    batch_id: UUID
    batch_name: str
    campus_name: str
    total_students: int
    avg_attendance_percentage: float
    attendance_trend: list[dict]


class CourseAnalytics(BaseModel):
    course_id: UUID
    course_name: str
    total_students: int
    avg_attendance_percentage: float


class OverallDashboard(BaseModel):
    total_students: int
    active_students: int
    total_campuses: int
    total_batches: int
    total_courses: int
    today_attendance_percentage: float
    weekly_attendance_trend: list[dict]
    campus_wise_stats: list[CampusAnalytics]
