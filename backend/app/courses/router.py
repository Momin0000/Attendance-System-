from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import date
from app.database.session import get_db
from app.models.models import Course, Batch
from app.core.security import get_current_user, get_admin_or_above

course_router = APIRouter(prefix="/courses", tags=["Courses"])
batch_router = APIRouter(prefix="/batches", tags=["Batches"])


# --- COURSES ---

class CourseCreate(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    duration_months: Optional[int] = None
    campus_id: int


class CourseResponse(BaseModel):
    id: int
    name: str
    code: str
    description: Optional[str]
    duration_months: Optional[int]
    campus_id: int
    is_active: bool

    class Config:
        from_attributes = True


@course_router.get("/", response_model=List[CourseResponse])
async def list_courses(
    campus_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    q = db.query(Course).filter(Course.is_deleted == False)
    if campus_id:
        q = q.filter(Course.campus_id == campus_id)
    return q.all()


@course_router.post("/", response_model=CourseResponse)
async def create_course(
    data: CourseCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_admin_or_above)
):
    course = Course(**data.model_dump())
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


@course_router.put("/{course_id}", response_model=CourseResponse)
async def update_course(
    course_id: int,
    data: CourseCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_admin_or_above)
):
    course = db.query(Course).filter(Course.id == course_id, Course.is_deleted == False).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    for k, v in data.model_dump().items():
        setattr(course, k, v)
    db.commit()
    db.refresh(course)
    return course


@course_router.delete("/{course_id}")
async def delete_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_admin_or_above)
):
    course = db.query(Course).filter(Course.id == course_id, Course.is_deleted == False).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    course.is_deleted = True
    db.commit()
    return {"message": "Course deleted"}


# --- BATCHES ---

class BatchCreate(BaseModel):
    name: str
    start_date: date
    end_date: Optional[date] = None
    campus_id: int
    course_id: int


class BatchResponse(BaseModel):
    id: int
    name: str
    start_date: date
    end_date: Optional[date]
    campus_id: int
    course_id: int
    is_active: bool

    class Config:
        from_attributes = True


@batch_router.get("/", response_model=List[BatchResponse])
async def list_batches(
    campus_id: Optional[int] = None,
    course_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    q = db.query(Batch).filter(Batch.is_deleted == False)
    if campus_id:
        q = q.filter(Batch.campus_id == campus_id)
    if course_id:
        q = q.filter(Batch.course_id == course_id)
    return q.all()


@batch_router.post("/", response_model=BatchResponse)
async def create_batch(
    data: BatchCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_admin_or_above)
):
    batch = Batch(**data.model_dump())
    db.add(batch)
    db.commit()
    db.refresh(batch)
    return batch


@batch_router.put("/{batch_id}", response_model=BatchResponse)
async def update_batch(
    batch_id: int,
    data: BatchCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_admin_or_above)
):
    batch = db.query(Batch).filter(Batch.id == batch_id, Batch.is_deleted == False).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    for k, v in data.model_dump().items():
        setattr(batch, k, v)
    db.commit()
    db.refresh(batch)
    return batch


@batch_router.delete("/{batch_id}")
async def delete_batch(
    batch_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_admin_or_above)
):
    batch = db.query(Batch).filter(Batch.id == batch_id, Batch.is_deleted == False).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    batch.is_deleted = True
    db.commit()
    return {"message": "Batch deleted"}
