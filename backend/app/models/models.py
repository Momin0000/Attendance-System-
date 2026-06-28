from sqlalchemy import (
    Column, String, Integer, Date, DateTime, Boolean,
    ForeignKey, Text, Enum, BigInteger, Index
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
import enum

Base = declarative_base()


class RoleEnum(str, enum.Enum):
    SUPER_ADMIN = "super_admin"
    CAMPUS_ADMIN = "campus_admin"
    TEACHER = "teacher"
    ATTENDANCE_OPERATOR = "attendance_operator"
    STUDENT = "student"


class GenderEnum(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class AttendanceStatusEnum(str, enum.Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(Enum(RoleEnum), nullable=False, default=RoleEnum.ATTENDANCE_OPERATOR)
    campus_id = Column(Integer, ForeignKey("campuses.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    campus = relationship("Campus", back_populates="users")
    activity_logs = relationship("ActivityLog", back_populates="user")


class Campus(Base):
    __tablename__ = "campuses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    code = Column(String(10), unique=True, nullable=False)  # e.g. KHI, LHR
    city = Column(String(100), nullable=False)
    address = Column(Text, nullable=True)
    phone = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    users = relationship("User", back_populates="campus")
    students = relationship("Student", back_populates="campus")
    courses = relationship("Course", back_populates="campus")
    batches = relationship("Batch", back_populates="campus")


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    code = Column(String(20), nullable=False)
    description = Column(Text, nullable=True)
    duration_months = Column(Integer, nullable=True)
    campus_id = Column(Integer, ForeignKey("campuses.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    campus = relationship("Campus", back_populates="courses")
    batches = relationship("Batch", back_populates="course")
    students = relationship("Student", back_populates="course")


class Batch(Base):
    __tablename__ = "batches"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    campus_id = Column(Integer, ForeignKey("campuses.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    campus = relationship("Campus", back_populates="batches")
    course = relationship("Course", back_populates="batches")
    students = relationship("Student", back_populates="batch")


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String(20), unique=True, nullable=False, index=True)  # BQ-KHI-000001
    full_name = Column(String(255), nullable=False)
    father_name = Column(String(255), nullable=True)
    cnic = Column(String(15), nullable=True)  # 42101-1234567-1
    phone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    gender = Column(Enum(GenderEnum), nullable=True)
    date_of_birth = Column(Date, nullable=True)
    address = Column(Text, nullable=True)
    photo_path = Column(String(500), nullable=True)
    campus_id = Column(Integer, ForeignKey("campuses.id"), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=False, index=True)
    enrollment_date = Column(Date, nullable=False, server_default=func.current_date())
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    campus = relationship("Campus", back_populates="students")
    course = relationship("Course", back_populates="students")
    batch = relationship("Batch", back_populates="students")
    qr_codes = relationship("QRCode", back_populates="student")
    id_cards = relationship("IDCard", back_populates="student")
    attendance_records = relationship("Attendance", back_populates="student")

    __table_args__ = (
        Index("ix_students_campus_batch", "campus_id", "batch_id"),
    )


class QRCode(Base):
    __tablename__ = "qr_codes"

    id = Column(Integer, primary_key=True, index=True)
    student_id_ref = Column(Integer, ForeignKey("students.id"), nullable=False)
    student_id_code = Column(String(20), nullable=False, index=True)  # BQ-KHI-000001
    qr_image_path = Column(String(500), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("Student", back_populates="qr_codes")


class IDCard(Base):
    __tablename__ = "id_cards"

    id = Column(Integer, primary_key=True, index=True)
    student_id_ref = Column(Integer, ForeignKey("students.id"), nullable=False)
    pdf_path = Column(String(500), nullable=False)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("Student", back_populates="id_cards")


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(BigInteger, primary_key=True, index=True)
    student_db_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    student_id_code = Column(String(20), nullable=False, index=True)
    campus_id = Column(Integer, ForeignKey("campuses.id"), nullable=False, index=True)
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=False, index=True)
    attendance_date = Column(Date, nullable=False, index=True)
    check_in_time = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(Enum(AttendanceStatusEnum), default=AttendanceStatusEnum.PRESENT)
    marked_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    notes = Column(Text, nullable=True)

    student = relationship("Student", back_populates="attendance_records")

    __table_args__ = (
        Index("ix_attendance_student_date", "student_db_id", "attendance_date"),
        Index("ix_attendance_campus_date", "campus_id", "attendance_date"),
    )


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)
    entity = Column(String(100), nullable=True)
    entity_id = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="activity_logs")
