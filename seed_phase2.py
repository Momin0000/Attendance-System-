"""
Phase 2 seed script.
Run: python seed_phase2.py
Requires Phase 1 seed to have been run first (campuses, batches, courses must exist).
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models.user import User
from app.models.student import Student
from app.services.student_service import create_student, _generate_qr_code
from app.schemas.student import StudentCreate
from passlib.context import CryptContext
from datetime import date
import uuid

Base.metadata.create_all(bind=engine)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def seed():
    db: Session = SessionLocal()

    # Check if admin already exists
    existing_admin = db.query(User).filter(User.username == "admin").first()
    if not existing_admin:
        admin = User(
            username="admin",
            email="admin@banoquabil.pk",
            hashed_password=pwd_context.hash("Admin@1234"),
            full_name="System Administrator",
            role="admin",
            is_active=True,
        )
        db.add(admin)
        db.commit()
        print("✅ Admin user created: username=admin, password=Admin@1234")
    else:
        print("ℹ️  Admin user already exists, skipping.")

    # Get first campus for seeding students
    from app.models.campus import Campus
    from app.models.batch import Batch
    from app.models.course import Course

    campus = db.query(Campus).first()
    batch = db.query(Batch).first()
    course = db.query(Course).first()

    if not campus or not batch or not course:
        print("⚠️  No campus/batch/course found. Run Phase 1 seed first.")
        db.close()
        return

    campus_code = campus.code if hasattr(campus, "code") else campus.name[:3].upper()

    sample_students = [
        {
            "first_name": "Ali",
            "last_name": "Hassan",
            "email": "ali.hassan@student.pk",
            "phone": "03001234567",
            "gender": "male",
            "enrollment_date": date(2024, 1, 15),
        },
        {
            "first_name": "Fatima",
            "last_name": "Malik",
            "email": "fatima.malik@student.pk",
            "phone": "03009876543",
            "gender": "female",
            "enrollment_date": date(2024, 1, 15),
        },
        {
            "first_name": "Usman",
            "last_name": "Raza",
            "email": "usman.raza@student.pk",
            "phone": "03121234567",
            "gender": "male",
            "enrollment_date": date(2024, 1, 15),
        },
    ]

    for s in sample_students:
        if db.query(Student).filter(Student.email == s["email"]).first():
            print(f"ℹ️  Student {s['email']} already exists, skipping.")
            continue

        data = StudentCreate(
            campus_id=campus.id,
            batch_id=batch.id,
            course_id=course.id,
            **s
        )
        student = create_student(db, data, campus_code)
        print(f"✅ Student created: {student.student_id} - {student.first_name} {student.last_name}")

    db.close()
    print("\n🎉 Phase 2 seed complete.")


if __name__ == "__main__":
    seed()
