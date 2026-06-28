"""
HOW TO UPDATE YOUR PHASE 1 backend/app/main.py
Copy-paste these additions into your existing main.py.
Add the new routers right after the existing include_router calls.
"""

# ADD THESE IMPORTS at the top of main.py:
from app.students.router import router as students_router
from app.attendance.router import router as attendance_router
from app.analytics.router import router as analytics_router
from app.reports.router import router as reports_router
from app.users.router import router as users_router

# ADD THESE LINES after the existing app.include_router(...) calls:
# app.include_router(students_router)
# app.include_router(attendance_router)
# app.include_router(analytics_router)
# app.include_router(reports_router)
# app.include_router(users_router)

# Also add this line for static file serving (photo/QR downloads):
# from fastapi.staticfiles import StaticFiles
# app.mount("/storage", StaticFiles(directory=settings.STORAGE_PATH), name="storage")

# ─────────────────────────────────────────────────────────────
# FULL UPDATED main.py (replace your existing one entirely):
# ─────────────────────────────────────────────────────────────

FULL_MAIN_PY = '''
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.core.config import settings
from app.database.session import engine, Base

# Phase 1 routers
from app.auth.router import router as auth_router
from app.campuses.router import router as campuses_router
from app.courses.router import router as courses_router
from app.batches.router import router as batches_router

# Phase 3 routers
from app.students.router import router as students_router
from app.attendance.router import router as attendance_router
from app.analytics.router import router as analytics_router
from app.reports.router import router as reports_router
from app.users.router import router as users_router

Base.metadata.create_all(bind=engine)

os.makedirs(os.path.join(settings.STORAGE_PATH, "photos"), exist_ok=True)
os.makedirs(os.path.join(settings.STORAGE_PATH, "qr_codes"), exist_ok=True)
os.makedirs(os.path.join(settings.STORAGE_PATH, "id_cards"), exist_ok=True)

app = FastAPI(
    title="Bano Qabil Attendance System",
    version="3.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/storage", StaticFiles(directory=settings.STORAGE_PATH), name="storage")

app.include_router(auth_router)
app.include_router(campuses_router)
app.include_router(courses_router)
app.include_router(batches_router)
app.include_router(students_router)
app.include_router(attendance_router)
app.include_router(analytics_router)
app.include_router(reports_router)
app.include_router(users_router)

@app.get("/health")
def health():
    return {"status": "ok", "version": "3.0.0"}
'''
