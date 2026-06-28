"""
Phase 3 - Users Router
Add to main.py: from app.users.router import router as users_router
                app.include_router(users_router)
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

from app.database.session import get_db
from app.models.models import User
from app.core.security import get_current_user, get_admin_or_above, get_password_hash, verify_password

router = APIRouter(prefix="/users", tags=["Users"])

VALID_ROLES = {"super_admin", "campus_admin", "teacher", "attendance_operator"}


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: str = "teacher"
    campus_id: Optional[int] = None


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[str] = None
    campus_id: Optional[int] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    campus_id: Optional[int]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    total: int
    users: List[UserResponse]


@router.get("/", response_model=UserListResponse)
async def list_users(
    role: Optional[str] = Query(None),
    campus_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_admin_or_above),
):
    q = db.query(User).filter(User.is_deleted == False)
    if role:
        q = q.filter(User.role == role)
    if campus_id:
        q = q.filter(User.campus_id == campus_id)
    users = q.order_by(User.id.desc()).all()
    return {"total": len(users), "users": users}


@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(
    data: UserCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_admin_or_above),
):
    if data.role not in VALID_ROLES:
        raise HTTPException(status_code=400, detail=f"Invalid role. Choose from: {VALID_ROLES}")
    if db.query(User).filter(User.email == data.email, User.is_deleted == False).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=data.email,
        hashed_password=get_password_hash(data.password),
        full_name=data.full_name,
        role=data.role,
        campus_id=data.campus_id,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/me", response_model=UserResponse)
async def get_me(current_user=Depends(get_current_user)):
    return current_user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_admin_or_above),
):
    user = db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_admin_or_above),
):
    user = db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if data.role and data.role not in VALID_ROLES:
        raise HTTPException(status_code=400, detail=f"Invalid role. Choose from: {VALID_ROLES}")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(user, k, v)
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=204)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_admin_or_above),
):
    user = db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot delete yourself")
    user.is_deleted = True
    db.commit()


@router.post("/{user_id}/reset-password", response_model=UserResponse)
async def reset_password(
    user_id: int,
    new_password: str = Query(..., min_length=6),
    db: Session = Depends(get_db),
    current_user=Depends(get_admin_or_above),
):
    user = db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.hashed_password = get_password_hash(new_password)
    db.commit()
    db.refresh(user)
    return user
