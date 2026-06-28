import uuid
from sqlalchemy import Column, String, Date, Boolean, ForeignKey, DateTime, Text, Time
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class AttendanceRecord(Base):
    __tablename__ = "attendance_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.id"), nullable=False)
    batch_id = Column(UUID(as_uuid=True), ForeignKey("batches.id"), nullable=False)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id"), nullable=False)
    campus_id = Column(UUID(as_uuid=True), ForeignKey("campuses.id"), nullable=False)

    attendance_date = Column(Date, nullable=False)
    check_in_time = Column(DateTime(timezone=True), nullable=True)
    check_out_time = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(20), default="present")  # present, absent, late
    scan_method = Column(String(20), default="qr")  # qr, manual
    notes = Column(Text, nullable=True)
    qr_token_used = Column(String(500), nullable=True)

    marked_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    student = relationship("Student", back_populates="attendance_records")
    batch = relationship("Batch")
    course = relationship("Course")
    campus = relationship("Campus")
