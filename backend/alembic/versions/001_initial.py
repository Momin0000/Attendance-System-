"""Initial migration - create all tables

Revision ID: 001_initial
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enums
    role_enum = sa.Enum(
        "super_admin", "campus_admin", "teacher", "attendance_operator", "student",
        name="roleenum"
    )
    gender_enum = sa.Enum("male", "female", "other", name="genderenum")
    status_enum = sa.Enum("present", "absent", "late", name="attendancestatusenum")

    role_enum.create(op.get_bind(), checkfirst=True)
    gender_enum.create(op.get_bind(), checkfirst=True)
    status_enum.create(op.get_bind(), checkfirst=True)

    # campuses
    op.create_table(
        "campuses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("code", sa.String(10), unique=True, nullable=False),
        sa.Column("city", sa.String(100), nullable=False),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true"),
        sa.Column("is_deleted", sa.Boolean(), server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # users
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("role", role_enum, nullable=False),
        sa.Column("campus_id", sa.Integer(), sa.ForeignKey("campuses.id"), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true"),
        sa.Column("is_deleted", sa.Boolean(), server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_users_email", "users", ["email"])

    # courses
    op.create_table(
        "courses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("code", sa.String(20), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("duration_months", sa.Integer(), nullable=True),
        sa.Column("campus_id", sa.Integer(), sa.ForeignKey("campuses.id"), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true"),
        sa.Column("is_deleted", sa.Boolean(), server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # batches
    op.create_table(
        "batches",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("campus_id", sa.Integer(), sa.ForeignKey("campuses.id"), nullable=False),
        sa.Column("course_id", sa.Integer(), sa.ForeignKey("courses.id"), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true"),
        sa.Column("is_deleted", sa.Boolean(), server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # students
    op.create_table(
        "students",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("student_id", sa.String(20), unique=True, nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("father_name", sa.String(255), nullable=True),
        sa.Column("cnic", sa.String(15), nullable=True),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("gender", gender_enum, nullable=True),
        sa.Column("date_of_birth", sa.Date(), nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("photo_path", sa.String(500), nullable=True),
        sa.Column("campus_id", sa.Integer(), sa.ForeignKey("campuses.id"), nullable=False),
        sa.Column("course_id", sa.Integer(), sa.ForeignKey("courses.id"), nullable=False),
        sa.Column("batch_id", sa.Integer(), sa.ForeignKey("batches.id"), nullable=False),
        sa.Column("enrollment_date", sa.Date(), server_default=sa.func.current_date()),
        sa.Column("is_active", sa.Boolean(), server_default="true"),
        sa.Column("is_deleted", sa.Boolean(), server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_students_student_id", "students", ["student_id"])
    op.create_index("ix_students_campus_id", "students", ["campus_id"])
    op.create_index("ix_students_batch_id", "students", ["batch_id"])
    op.create_index("ix_students_campus_batch", "students", ["campus_id", "batch_id"])

    # qr_codes
    op.create_table(
        "qr_codes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("student_id_ref", sa.Integer(), sa.ForeignKey("students.id"), nullable=False),
        sa.Column("student_id_code", sa.String(20), nullable=False),
        sa.Column("qr_image_path", sa.String(500), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_qr_student_id_code", "qr_codes", ["student_id_code"])

    # id_cards
    op.create_table(
        "id_cards",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("student_id_ref", sa.Integer(), sa.ForeignKey("students.id"), nullable=False),
        sa.Column("pdf_path", sa.String(500), nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # attendance
    op.create_table(
        "attendance",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("student_db_id", sa.Integer(), sa.ForeignKey("students.id"), nullable=False),
        sa.Column("student_id_code", sa.String(20), nullable=False),
        sa.Column("campus_id", sa.Integer(), sa.ForeignKey("campuses.id"), nullable=False),
        sa.Column("batch_id", sa.Integer(), sa.ForeignKey("batches.id"), nullable=False),
        sa.Column("attendance_date", sa.Date(), nullable=False),
        sa.Column("check_in_time", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("status", status_enum, server_default="present"),
        sa.Column("marked_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
    )
    op.create_index("ix_attendance_student_date", "attendance", ["student_db_id", "attendance_date"])
    op.create_index("ix_attendance_campus_date", "attendance", ["campus_id", "attendance_date"])
    op.create_index("ix_attendance_date", "attendance", ["attendance_date"])

    # activity_logs
    op.create_table(
        "activity_logs",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("entity", sa.String(100), nullable=True),
        sa.Column("entity_id", sa.Integer(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("activity_logs")
    op.drop_table("attendance")
    op.drop_table("id_cards")
    op.drop_table("qr_codes")
    op.drop_table("students")
    op.drop_table("batches")
    op.drop_table("courses")
    op.drop_table("users")
    op.drop_table("campuses")

    op.execute("DROP TYPE IF EXISTS attendancestatusenum")
    op.execute("DROP TYPE IF EXISTS genderenum")
    op.execute("DROP TYPE IF EXISTS roleenum")
