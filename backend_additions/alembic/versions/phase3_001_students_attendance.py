"""Phase 3: students full, attendance_records, qr_codes, id_cards

Revision ID: phase3_001
Revises: <your_phase1_revision_id>
"""
from alembic import op
import sqlalchemy as sa

revision = "phase3_001"
down_revision = None  # ← SET THIS to your Phase 1 latest revision ID
branch_labels = None
depends_on = None


def upgrade():
    # Add new columns to students table
    with op.batch_alter_table("students") as batch_op:
        batch_op.add_column(sa.Column("full_name", sa.String(200), nullable=True))
        batch_op.add_column(sa.Column("father_name", sa.String(200), nullable=True))
        batch_op.add_column(sa.Column("cnic", sa.String(20), nullable=True))
        batch_op.add_column(sa.Column("phone", sa.String(20), nullable=True))
        batch_op.add_column(sa.Column("email", sa.String(255), nullable=True))
        batch_op.add_column(sa.Column("gender", sa.String(10), nullable=True))
        batch_op.add_column(sa.Column("date_of_birth", sa.Date(), nullable=True))
        batch_op.add_column(sa.Column("address", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("photo_path", sa.String(500), nullable=True))
        batch_op.add_column(sa.Column("enrollment_date", sa.Date(), nullable=True))
        batch_op.add_column(sa.Column("is_active", sa.Boolean(), server_default="true"))
        batch_op.add_column(sa.Column("is_deleted", sa.Boolean(), server_default="false"))
        batch_op.add_column(sa.Column("student_id", sa.String(20), nullable=True))

    # Create unique index for student_id
    op.create_index("ix_students_student_id", "students", ["student_id"], unique=True)

    # Add is_deleted to users if missing
    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(sa.Column("is_deleted", sa.Boolean(), server_default="false"))

    # attendance_records
    op.create_table(
        "attendance_records",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("student_db_id", sa.Integer(), sa.ForeignKey("students.id"), nullable=False),
        sa.Column("student_id_code", sa.String(20), nullable=False),
        sa.Column("campus_id", sa.Integer(), sa.ForeignKey("campuses.id"), nullable=False),
        sa.Column("batch_id", sa.Integer(), sa.ForeignKey("batches.id"), nullable=False),
        sa.Column("attendance_date", sa.Date(), nullable=False),
        sa.Column("check_in_time", sa.DateTime(), nullable=True),
        sa.Column("check_out_time", sa.DateTime(), nullable=True),
        sa.Column("status", sa.String(20), server_default="present"),
        sa.Column("scan_method", sa.String(20), server_default="qr"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("marked_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index("ix_attendance_date", "attendance_records", ["attendance_date"])
    op.create_index("ix_attendance_student", "attendance_records", ["student_db_id"])

    # qr_codes
    op.create_table(
        "qr_codes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("student_id_ref", sa.Integer(), sa.ForeignKey("students.id"), nullable=False),
        sa.Column("student_id_code", sa.String(20), nullable=False),
        sa.Column("qr_image_path", sa.String(500), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true"),
        sa.Column("generated_at", sa.DateTime(), server_default=sa.func.now()),
    )

    # id_cards
    op.create_table(
        "id_cards",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("student_id_ref", sa.Integer(), sa.ForeignKey("students.id"), nullable=False),
        sa.Column("pdf_path", sa.String(500), nullable=False),
        sa.Column("generated_at", sa.DateTime(), server_default=sa.func.now()),
    )


def downgrade():
    op.drop_table("id_cards")
    op.drop_table("qr_codes")
    op.drop_table("attendance_records")
    op.drop_index("ix_students_student_id", table_name="students")
    with op.batch_alter_table("students") as batch_op:
        for col in ["student_id", "is_deleted", "is_active", "enrollment_date",
                    "photo_path", "address", "date_of_birth", "gender",
                    "email", "phone", "cnic", "father_name", "full_name"]:
            batch_op.drop_column(col)
