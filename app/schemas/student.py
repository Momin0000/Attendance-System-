from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import date, datetime
from uuid import UUID


class StudentBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    cnic: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    campus_id: UUID
    batch_id: UUID
    course_id: UUID
    enrollment_date: Optional[date] = None

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v):
        if v and v not in ["male", "female", "other"]:
            raise ValueError("gender must be male, female, or other")
        return v


class StudentCreate(StudentBase):
    pass


class StudentUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    cnic: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    batch_id: Optional[UUID] = None
    course_id: Optional[UUID] = None
    enrollment_date: Optional[date] = None
    is_active: Optional[bool] = None


class StudentResponse(StudentBase):
    id: UUID
    student_id: str
    photo_path: Optional[str] = None
    qr_code_path: Optional[str] = None
    id_card_path: Optional[str] = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class StudentListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    students: list[StudentResponse]
