from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, require_role
from app.schemas.user import UserCreate, UserUpdate, UserPasswordChange, UserResponse, UserListResponse
from app.services import user_service

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserResponse, status_code=201)
def create_user(
    data: UserCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["admin"])),
):
    return user_service.create_user(db, data)


@router.get("/", response_model=UserListResponse)
def list_users(
    role: Optional[str] = Query(None),
    campus_id: Optional[UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["admin"])),
):
    total, users = user_service.list_users(db, role, campus_id)
    return {"total": total, "users": users}


@router.get("/me", response_model=UserResponse)
def get_me(current_user=Depends(get_current_user)):
    return current_user


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["admin"])),
):
    return user_service.get_user(db, user_id)


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: UUID,
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["admin"])),
):
    return user_service.update_user(db, user_id, data)


@router.delete("/{user_id}", status_code=204)
def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["admin"])),
):
    user_service.delete_user(db, user_id)


@router.post("/me/change-password", response_model=UserResponse)
def change_my_password(
    data: UserPasswordChange,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return user_service.change_password(db, current_user.id, data.current_password, data.new_password)


@router.post("/{user_id}/reset-password", response_model=UserResponse)
def admin_reset_password(
    user_id: UUID,
    new_password: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["admin"])),
):
    return user_service.admin_reset_password(db, user_id, new_password)
