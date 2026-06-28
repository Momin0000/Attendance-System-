from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.database import engine, Base

# Import all models so SQLAlchemy registers them
from app.models import student, attendance, user  # noqa

# Import Phase 1 models too (campus, batch, course)
# from app.models import campus, batch, course  # already defined in Phase 1

from app.routers import auth, students, attendance as attendance_router, analytics, reports, users

# Create tables (use Alembic in production instead)
Base.metadata.create_all(bind=engine)

os.makedirs("uploads/photos", exist_ok=True)
os.makedirs("uploads/qr_codes", exist_ok=True)
os.makedirs("uploads/id_cards", exist_ok=True)
os.makedirs("reports", exist_ok=True)

app = FastAPI(
    title="Bano Qabil Pakistan - Attendance System",
    description="Student Attendance Management System - Phase 2",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for uploaded photos/QR
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Register routers
app.include_router(auth.router)
app.include_router(students.router)
app.include_router(attendance_router.router)
app.include_router(analytics.router)
app.include_router(reports.router)
app.include_router(users.router)


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "Bano Qabil Attendance System - Phase 2 Running"}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}
