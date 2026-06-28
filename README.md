# Bano Qabil — Phase 3 Complete Setup Guide

## What Phase 3 Adds
- Full Next.js 14 frontend (TypeScript + Tailwind CSS)
- Dashboard with charts (recharts)
- Students page: full CRUD, photo upload, QR download, ID card PDF
- Attendance page: live QR scanner (camera) + manual entry + daily records
- Reports page: download Excel, CSV, PDF
- Settings page: manage campuses, courses, batches
- Users page: admin user management + password reset
- Backend routers: students, attendance, analytics, reports, users

---

## FOLDER STRUCTURE AFTER PHASE 3

```
bq-attendance/                        ← your root project folder
├── backend/                          ← Phase 1 backend (unchanged except main.py additions)
│   ├── app/
│   │   ├── main.py                   ← UPDATE THIS (see instructions below)
│   │   ├── models/models.py          ← UPDATE THIS (add new columns/tables)
│   │   ├── students/router.py        ← NEW from phase3/backend_additions
│   │   ├── attendance/router.py      ← NEW from phase3/backend_additions
│   │   ├── analytics/router.py       ← NEW from phase3/backend_additions
│   │   ├── reports/router.py         ← NEW from phase3/backend_additions
│   │   └── users/router.py           ← NEW from phase3/backend_additions
│   ├── alembic/
│   │   └── versions/
│   │       └── phase3_001_...py      ← NEW migration
│   └── requirements.txt              ← ADD new packages (see below)
├── frontend/                         ← Phase 3 frontend (everything new)
│   ├── app/
│   ├── components/
│   ├── lib/
│   ├── store/
│   ├── types/
│   ├── utils/
│   ├── package.json
│   └── .env.local
└── docker-compose.yml                ← REPLACE with phase3 version
```

---

## STEP 1 — Copy Phase 3 backend files into your backend folder

```cmd
cd C:\path\to\bq-attendance

REM Copy new routers into backend
xcopy /E /I phase3\backend_additions\app\students backend\app\students
xcopy /E /I phase3\backend_additions\app\attendance backend\app\attendance
xcopy /E /I phase3\backend_additions\app\analytics backend\app\analytics
xcopy /E /I phase3\backend_additions\app\reports backend\app\reports
xcopy /E /I phase3\backend_additions\app\users backend\app\users

REM Copy migration
copy phase3\backend_additions\alembic\versions\phase3_001_students_attendance.py backend\alembic\versions\

REM Copy frontend
xcopy /E /I phase3\frontend frontend
```

On Linux/macOS:
```bash
cd /path/to/bq-attendance
cp -r phase3/backend_additions/app/students backend/app/students
cp -r phase3/backend_additions/app/attendance backend/app/attendance
cp -r phase3/backend_additions/app/analytics backend/app/analytics
cp -r phase3/backend_additions/app/reports backend/app/reports
cp -r phase3/backend_additions/app/users backend/app/users
cp phase3/backend_additions/alembic/versions/phase3_001_students_attendance.py backend/alembic/versions/
cp -r phase3/frontend frontend
```

---

## STEP 2 — Update backend/app/models/models.py

Open `backend/app/models/models.py` and add these to the EXISTING classes:

### To Student class — add these columns:
```python
full_name       = Column(String(200), nullable=False)
father_name     = Column(String(200), nullable=True)
cnic            = Column(String(20), unique=True, nullable=True)
phone           = Column(String(20), nullable=True)
email           = Column(String(255), nullable=True)
gender          = Column(String(10), nullable=True)
date_of_birth   = Column(Date, nullable=True)
address         = Column(Text, nullable=True)
photo_path      = Column(String(500), nullable=True)
enrollment_date = Column(Date, nullable=True)
is_active       = Column(Boolean, default=True)
is_deleted      = Column(Boolean, default=False)
student_id      = Column(String(20), unique=True, nullable=True)
```

### To User class — add:
```python
is_deleted = Column(Boolean, default=False)
```

### Add entirely new classes at the bottom of the file:
```python
class AttendanceRecord(Base):
    __tablename__ = "attendance_records"
    id              = Column(Integer, primary_key=True, index=True)
    student_db_id   = Column(Integer, ForeignKey("students.id"), nullable=False)
    student_id_code = Column(String(20), nullable=False, index=True)
    campus_id       = Column(Integer, ForeignKey("campuses.id"), nullable=False)
    batch_id        = Column(Integer, ForeignKey("batches.id"), nullable=False)
    attendance_date = Column(Date, nullable=False, index=True)
    check_in_time   = Column(DateTime, nullable=True)
    check_out_time  = Column(DateTime, nullable=True)
    status          = Column(String(20), default="present")
    scan_method     = Column(String(20), default="qr")
    notes           = Column(Text, nullable=True)
    marked_by       = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at      = Column(DateTime, server_default=func.now())

class QRCode(Base):
    __tablename__ = "qr_codes"
    id              = Column(Integer, primary_key=True, index=True)
    student_id_ref  = Column(Integer, ForeignKey("students.id"), nullable=False)
    student_id_code = Column(String(20), nullable=False)
    qr_image_path   = Column(String(500), nullable=False)
    is_active       = Column(Boolean, default=True)
    generated_at    = Column(DateTime, server_default=func.now())

class IDCard(Base):
    __tablename__ = "id_cards"
    id             = Column(Integer, primary_key=True, index=True)
    student_id_ref = Column(Integer, ForeignKey("students.id"), nullable=False)
    pdf_path       = Column(String(500), nullable=False)
    generated_at   = Column(DateTime, server_default=func.now())
```

---

## STEP 3 — Update backend/app/main.py

Add these imports near the top:
```python
from fastapi.staticfiles import StaticFiles
from app.students.router import router as students_router
from app.attendance.router import router as attendance_router
from app.analytics.router import router as analytics_router
from app.reports.router import router as reports_router
from app.users.router import router as users_router
```

Add these lines after your existing `app.include_router(...)` calls:
```python
app.include_router(students_router)
app.include_router(attendance_router)
app.include_router(analytics_router)
app.include_router(reports_router)
app.include_router(users_router)
app.mount("/storage", StaticFiles(directory=settings.STORAGE_PATH), name="storage")
```

Also update CORS to include the frontend:
```python
allow_origins=["http://localhost:3000"]
```

---

## STEP 4 — Add new Python packages to backend

```cmd
cd backend
venv\Scripts\activate
pip install qrcode[pil] Pillow reportlab openpyxl
pip freeze > requirements.txt
```

On Linux/macOS:
```bash
cd backend
source venv/bin/activate
pip install qrcode[pil] Pillow reportlab openpyxl
pip freeze > requirements.txt
```

---

## STEP 5 — Fix the migration down_revision

Open: `backend/alembic/versions/phase3_001_students_attendance.py`

Find this line:
```python
down_revision = None  # ← SET THIS
```

Replace `None` with your Phase 1 revision ID. To find it:
```cmd
cd backend
alembic history
```

Copy the revision ID from Phase 1 (looks like `a1b2c3d4e5f6`) and set:
```python
down_revision = "a1b2c3d4e5f6"
```

---

## STEP 6 — Run the migration

```cmd
cd backend
alembic upgrade head
```

Expected output:
```
INFO  [alembic.runtime.migration] Running upgrade a1b2c3d4e5f6 -> phase3_001, Phase 3: students...
```

---

## STEP 7 — Start the backend

```cmd
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

On Linux/macOS:
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Verify it works: open http://localhost:8000/docs — you should see the new endpoints.

---

## STEP 8 — Install and run the frontend

Open a NEW terminal window (keep backend running):

```cmd
cd frontend
npm install
npm run dev
```

On Linux/macOS:
```bash
cd frontend
npm install
npm run dev
```

Open browser: http://localhost:3000

Login with:
- Email: admin@banoquabil.pk
- Password: Admin@12345

---

## STEP 9 — Running with Docker (both backend + frontend together)

If you prefer Docker instead of Steps 7–8:

```cmd
cd bq-attendance
docker-compose up --build
```

Wait 2 minutes for everything to start. Then:
- Frontend: http://localhost:3000
- Backend API docs: http://localhost:8000/docs

---

## GIT COMMANDS — Push Everything to GitHub

```cmd
cd C:\path\to\bq-attendance

git add .

git commit -m "feat: Phase 3 - Next.js frontend + students/attendance/analytics/reports/users backend modules"

git push origin main
```

If you have not set up Git remote yet:
```cmd
git init
git add .
git commit -m "feat: Phase 3 complete"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/bano-qabil-attendance.git
git push -u origin main
```

Replace YOUR_USERNAME with your actual GitHub username.

---

## COMMON ERRORS AND FIXES

**Frontend: `Module not found: axios`**
```cmd
cd frontend
npm install
```

**Frontend shows blank page**
Check that backend is running on port 8000. Check browser console for CORS errors.

**Backend: `ModuleNotFoundError: app.students`**
Make sure you copied the files in Step 1. Check the folder exists: `backend/app/students/router.py`

**Alembic: `Target database is not up to date`**
```cmd
cd backend
alembic stamp head
alembic upgrade head
```

**QR scanner not opening camera**
Browser requires HTTPS or localhost for camera access. You are on localhost so it will work. If on a different IP, use HTTPS.

**`relation attendance_records does not exist`**
You skipped Step 6. Run the migration:
```cmd
cd backend
alembic upgrade head
```

**Student ID not generating**
Check that your Campus model has a `code` field. If not, open `backend/app/students/router.py` and change:
```python
campus_code = campus.code
```
to:
```python
campus_code = campus.name[:3].upper()
```
