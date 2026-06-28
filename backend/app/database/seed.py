"""
Seed script — run once after migrations.
Creates a Super Admin user and sample campus/course/batch data.

Usage:
    python -m app.database.seed
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.database.session import SessionLocal
from app.models.models import User, Campus, Course, Batch, RoleEnum
from app.core.security import get_password_hash
from datetime import date


def seed():
    db = SessionLocal()
    try:
        # Skip if already seeded
        if db.query(User).filter(User.role == RoleEnum.SUPER_ADMIN).first():
            print("✓ Already seeded. Skipping.")
            return

        # 1. Campuses
        karachi = Campus(name="Karachi Campus", code="KHI", city="Karachi",
                         address="Block 14, Gulshan-e-Iqbal, Karachi", phone="021-111222333")
        lahore = Campus(name="Lahore Campus", code="LHR", city="Lahore",
                        address="Model Town, Lahore", phone="042-111222333")
        islamabad = Campus(name="Islamabad Campus", code="ISB", city="Islamabad",
                           address="F-10 Markaz, Islamabad", phone="051-111222333")
        db.add_all([karachi, lahore, islamabad])
        db.flush()

        # 2. Courses
        web_dev = Course(name="Web & App Development", code="WAD",
                         description="Full stack web and mobile app development",
                         duration_months=6, campus_id=karachi.id)
        python_ai = Course(name="Python & AI", code="PAI",
                           description="Python programming with AI/ML",
                           duration_months=3, campus_id=karachi.id)
        graphic = Course(name="Graphic Design", code="GRD",
                         description="Adobe suite and design fundamentals",
                         duration_months=3, campus_id=lahore.id)
        db.add_all([web_dev, python_ai, graphic])
        db.flush()

        # 3. Batches
        batch1 = Batch(name="Batch-01 2024", start_date=date(2024, 1, 15),
                       end_date=date(2024, 7, 15), campus_id=karachi.id, course_id=web_dev.id)
        batch2 = Batch(name="Batch-02 2024", start_date=date(2024, 7, 1),
                       end_date=date(2025, 1, 1), campus_id=karachi.id, course_id=python_ai.id)
        db.add_all([batch1, batch2])
        db.flush()

        # 4. Super Admin user
        super_admin = User(
            email="admin@banoquabil.pk",
            hashed_password=get_password_hash("Admin@12345"),
            full_name="Super Administrator",
            role=RoleEnum.SUPER_ADMIN,
        )

        # 5. Campus Admin
        campus_admin = User(
            email="khi.admin@banoquabil.pk",
            hashed_password=get_password_hash("Admin@12345"),
            full_name="Karachi Campus Admin",
            role=RoleEnum.CAMPUS_ADMIN,
            campus_id=karachi.id,
        )

        # 6. Attendance Operator
        operator = User(
            email="operator@banoquabil.pk",
            hashed_password=get_password_hash("Admin@12345"),
            full_name="Attendance Operator",
            role=RoleEnum.ATTENDANCE_OPERATOR,
            campus_id=karachi.id,
        )

        db.add_all([super_admin, campus_admin, operator])
        db.commit()

        print("✓ Seed complete!")
        print("\n--- LOGIN CREDENTIALS ---")
        print("Super Admin : admin@banoquabil.pk        / Admin@12345")
        print("Campus Admin: khi.admin@banoquabil.pk   / Admin@12345")
        print("Operator    : operator@banoquabil.pk    / Admin@12345")
        print("--------------------------\n")

    except Exception as e:
        db.rollback()
        print(f"✗ Seed failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
