import uuid
from sqlalchemy import Column, String, Date, Boolean, ForeignKey, DateTime, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(String(20), unique=True, nullable=False, index=True)  # BQ-KHI-000001
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20), nullable=True)
    cnic = Column(String(15), unique=True, nullable=True)
    date_of_birth = Column(Date, nullable=True)
    gender = Column(String(10), nullable=True)
    address = Column(Text, nullable=True)
    photo_path = Column(String(500), nullable=True)
    qr_code_path = Column(String(500), nullable=True)
    id_card_path = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)

    campus_id = Column(UUID(as_uuid=True), ForeignKey("campuses.id"), nullable=False)
    batch_id = Column(UUID(as_uuid=True), ForeignKey("batches.id"), nullable=False)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id"), nullable=False)

    enrollment_date = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    campus = relationship("Campus", back_populates="students")
    batch = relationship("Batch", back_populates="students")
    course = relationship("Course", back_populates="students")
    attendance_records = relationship("AttendanceRecord", back_populates="student")
