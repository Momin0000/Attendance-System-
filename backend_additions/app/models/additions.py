"""
Phase 3 — Additional SQLAlchemy model columns/tables.
These are ADDITIONS to your Phase 1 models.py.

INSTRUCTIONS:
1. Open your Phase 1 file: backend/app/models/models.py
2. Add the columns marked below to the existing classes.
3. Add the new classes entirely.
4. Then run: alembic revision --autogenerate -m "phase3_students_attendance"
             alembic upgrade head
"""

# ─────────────────────────────────────────────────────────────
# ADD these columns to your existing Student model:
# ─────────────────────────────────────────────────────────────
"""
class Student(Base):
    __tablename__ = "students"
    ...existing Phase 1 columns...

    # ADD THESE:
    full_name       = Column(String(200), nullable=False)
    father_name     = Column(String(200), nullable=True)
    cnic            = Column(String(20), unique=True, nullable=True)
    phone           = Column(String(20), nullable=True)
    email           = Column(String(255), unique=True, nullable=True)
    gender          = Column(String(10), nullable=True)
    date_of_birth   = Column(Date, nullable=True)
    address         = Column(Text, nullable=True)
    photo_path      = Column(String(500), nullable=True)
    campus_id       = Column(Integer, ForeignKey("campuses.id"), nullable=False)
    course_id       = Column(Integer, ForeignKey("courses.id"), nullable=False)
    batch_id        = Column(Integer, ForeignKey("batches.id"), nullable=False)
    enrollment_date = Column(Date, default=date.today)
    is_active       = Column(Boolean, default=True)
    is_deleted      = Column(Boolean, default=False)
    student_id      = Column(String(20), unique=True, nullable=False)  # BQ-KHI-000001

    campus  = relationship("Campus", back_populates="students")
    course  = relationship("Course", back_populates="students")
    batch   = relationship("Batch", back_populates="students")
    qr_codes         = relationship("QRCode", back_populates="student")
    id_cards         = relationship("IDCard", back_populates="student")
    attendance_records = relationship("AttendanceRecord", back_populates="student")
"""

# ─────────────────────────────────────────────────────────────
# ADD these back-references to Campus, Course, Batch models:
# ─────────────────────────────────────────────────────────────
"""
class Campus(Base):
    ...
    students = relationship("Student", back_populates="campus")

class Course(Base):
    ...
    students = relationship("Student", back_populates="course")

class Batch(Base):
    ...
    students = relationship("Student", back_populates="batch")
"""

# ─────────────────────────────────────────────────────────────
# ADD these NEW tables entirely:
# ─────────────────────────────────────────────────────────────
from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
# Import Base from your Phase 1 database setup:
# from app.database.session import Base


class AttendanceRecord:  # Replace with Base properly in your file
    __tablename__ = "attendance_records"

    id               = Column(Integer, primary_key=True, index=True)
    student_db_id    = Column(Integer, ForeignKey("students.id"), nullable=False)
    student_id_code  = Column(String(20), nullable=False, index=True)
    campus_id        = Column(Integer, ForeignKey("campuses.id"), nullable=False)
    batch_id         = Column(Integer, ForeignKey("batches.id"), nullable=False)
    attendance_date  = Column(Date, nullable=False, index=True)
    check_in_time    = Column(DateTime, nullable=True)
    check_out_time   = Column(DateTime, nullable=True)
    status           = Column(String(20), default="present")   # present | absent | late
    scan_method      = Column(String(20), default="qr")        # qr | manual
    notes            = Column(Text, nullable=True)
    marked_by        = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at       = Column(DateTime, server_default=func.now())

    # student = relationship("Student", back_populates="attendance_records")


class QRCode:  # Replace with Base properly
    __tablename__ = "qr_codes"

    id               = Column(Integer, primary_key=True, index=True)
    student_id_ref   = Column(Integer, ForeignKey("students.id"), nullable=False)
    student_id_code  = Column(String(20), nullable=False)
    qr_image_path    = Column(String(500), nullable=False)
    is_active        = Column(Boolean, default=True)
    generated_at     = Column(DateTime, server_default=func.now())

    # student = relationship("Student", back_populates="qr_codes")


class IDCard:  # Replace with Base properly
    __tablename__ = "id_cards"

    id               = Column(Integer, primary_key=True, index=True)
    student_id_ref   = Column(Integer, ForeignKey("students.id"), nullable=False)
    pdf_path         = Column(String(500), nullable=False)
    generated_at     = Column(DateTime, server_default=func.now())

    # student = relationship("Student", back_populates="id_cards")


# ─────────────────────────────────────────────────────────────
# ADD to User model:
# ─────────────────────────────────────────────────────────────
"""
class User(Base):
    ...
    is_deleted = Column(Boolean, default=False)  # if not already there
"""
