from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os
from pathlib import Path
from app.core.config import settings
from app.models.models import Base
from app.database.session import engine
from app.auth.router import router as auth_router
from app.campuses.router import router as campus_router
from app.courses.router import course_router, batch_router
from app.students.router import router as students_router
from app.attendance.router import router as attendance_router
from app.analytics.router import router as analytics_router
from app.reports.router import router as reports_router
from app.users.router import router as users_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    for folder in ["qrcodes", "photos", "idcards"]:
        Path(settings.STORAGE_PATH, folder).mkdir(parents=True, exist_ok=True)
    yield

app = FastAPI(
    title=settings.APP_NAME,
    version="3.0.0",
    description="Student Attendance Management System for Bano Qabil",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

storage_path = Path(settings.STORAGE_PATH)
storage_path.mkdir(parents=True, exist_ok=True)
app.mount("/storage", StaticFiles(directory=str(storage_path)), name="storage")

app.include_router(auth_router)
app.include_router(campus_router)
app.include_router(course_router)
app.include_router(batch_router)
app.include_router(students_router)
app.include_router(attendance_router)
app.include_router(analytics_router)
app.include_router(reports_router)
app.include_router(users_router)

@app.get("/health")
async def health_check():
    return {"status": "ok", "app": settings.APP_NAME}

@app.get("/")
async def root():
    return {"message": "Bano Qabil Attendance System API", "docs": "/docs"}
