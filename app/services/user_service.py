from uuid import UUID
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from passlib.context import CryptContext

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user(db: Session, user_id: UUID) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def list_users(db: Session, role: Optional[str] = None, campus_id: Optional[UUID] = None):
    query = db.query(User)
    if role:
        query = query.filter(User.role == role)
    if campus_id:
        query = query.filter(User.campus_id == campus_id)
    users = query.all()
    return len(users), users


def create_user(db: Session, data: UserCreate) -> User:
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    valid_roles = {"admin", "instructor", "student"}
    if data.role not in valid_roles:
        raise HTTPException(status_code=400, detail=f"Role must be one of: {valid_roles}")

    hashed = pwd_context.hash(data.password)
    user = User(
        username=data.username,
        email=data.email,
        hashed_password=hashed,
        full_name=data.full_name,
        role=data.role,
        campus_id=data.campus_id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user_id: UUID, data: UserUpdate) -> User:
    user = get_user(db, user_id)
    update_data = data.model_dump(exclude_unset=True)

    if "role" in update_data:
        valid_roles = {"admin", "instructor", "student"}
        if update_data["role"] not in valid_roles:
            raise HTTPException(status_code=400, detail=f"Role must be one of: {valid_roles}")

    for key, val in update_data.items():
        setattr(user, key, val)

    db.commit()
    db.refresh(user)
    return user


def change_password(db: Session, user_id: UUID, current_password: str, new_password: str) -> User:
    user = get_user(db, user_id)
    if not pwd_context.verify(current_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    user.hashed_password = pwd_context.hash(new_password)
    db.commit()
    return user


def delete_user(db: Session, user_id: UUID):
    user = get_user(db, user_id)
    db.delete(user)
    db.commit()


def admin_reset_password(db: Session, user_id: UUID, new_password: str) -> User:
    user = get_user(db, user_id)
    user.hashed_password = pwd_context.hash(new_password)
    db.commit()
    return user
