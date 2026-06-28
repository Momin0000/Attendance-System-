@echo off  
start "Backend" cmd /k "cd E:\bq-attendence\backend && venv\Scripts\activate && uvicorn app.main:app --host 0.0.0.0 --port 8000"  
timeout /t 8  
start "Frontend" cmd /k "cd E:\bq-attendence\frontend && npm run dev"  
timeout /t 8  
start chrome http://localhost:3000  
