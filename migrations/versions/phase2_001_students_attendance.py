"""Phase 2: students and attendance tables

Revision ID: phase2_001
Revises: phase1_latest
Create Date: 2024-01-01
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'phase2_001'
down_revision = None  # Set this to your Phase 1 latest revision ID
branch_labels = None
depends_on = None


def upgrade():
    # Students table
    op.create_table(
        'students',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('student_id', sa.String(20), unique=True, nullable=False),
        sa.Column('first_name', sa.String(100), nullable=False),
        sa.Column('last_name', sa.String(100), nullable=False),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('cnic', sa.String(15), unique=True, nullable=True),
        sa.Column('date_of_birth', sa.Date(), nullable=True),
        sa.Column('gender', sa.String(10), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('photo_path', sa.String(500), nullable=True),
        sa.Column('qr_code_path', sa.String(500), nullable=True),
        sa.Column('id_card_path', sa.String(500), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('campus_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('campuses.id'), nullable=False),
        sa.Column('batch_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('batches.id'), nullable=False),
        sa.Column('course_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('courses.id'), nullable=False),
        sa.Column('enrollment_date', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )
    op.create_index('ix_students_student_id', 'students', ['student_id'])
    op.create_index('ix_students_email', 'students', ['email'])

    # Attendance records table
    op.create_table(
        'attendance_records',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('student_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('students.id'), nullable=False),
        sa.Column('batch_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('batches.id'), nullable=False),
        sa.Column('course_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('courses.id'), nullable=False),
        sa.Column('campus_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('campuses.id'), nullable=False),
        sa.Column('attendance_date', sa.Date(), nullable=False),
        sa.Column('check_in_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('check_out_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(20), default='present'),
        sa.Column('scan_method', sa.String(20), default='qr'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('qr_token_used', sa.String(500), nullable=True),
        sa.Column('marked_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )
    op.create_index('ix_attendance_date', 'attendance_records', ['attendance_date'])
    op.create_index('ix_attendance_student', 'attendance_records', ['student_id'])


def downgrade():
    op.drop_table('attendance_records')
    op.drop_table('students')
