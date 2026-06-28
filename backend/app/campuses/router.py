from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from app.database.session import get_db
from app.models.models import Campus
from app.core.security import get_current_user, get_admin_or_above

router = APIRouter(prefix="/campuses", tags=["Campuses"])


class CampusCreate(BaseModel):
    name: str
    code: str
    city: str
    address: Optional[str] = None
    phone: Optional[str] = None


class CampusResponse(BaseModel):
    id: int
    name: str
    code: str
    city: str
    address: Optional[str]
    phone: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True


@router.get("/", response_model=List[CampusResponse])
async def list_campuses(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return db.query(Campus).filter(Campus.is_deleted == False).all()


@router.post("/", response_model=CampusResponse)
async def create_campus(
    data: CampusCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_admin_or_above)
):
    existing = db.query(Campus).filter(Campus.code == data.code.upper()).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Campus code '{data.code}' already exists")

    campus = Campus(
        name=data.name,
        code=data.code.upper(),
        city=data.city,
        address=data.address,
        phone=data.phone,
    )
    db.add(campus)
    db.commit()
    db.refresh(campus)
    return campus


@router.get("/{campus_id}", response_model=CampusResponse)
async def get_campus(
    campus_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    campus = db.query(Campus).filter(Campus.id == campus_id, Campus.is_deleted == False).first()
    if not campus:
        raise HTTPException(status_code=404, detail="Campus not found")
    return campus


@router.put("/{campus_id}", response_model=CampusResponse)
async def update_campus(
    campus_id: int,
    data: CampusCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_admin_or_above)
):
    campus = db.query(Campus).filter(Campus.id == campus_id, Campus.is_deleted == False).first()
    if not campus:
        raise HTTPException(status_code=404, detail="Campus not found")

    campus.name = data.name
    campus.code = data.code.upper()
    campus.city = data.city
    campus.address = data.address
    campus.phone = data.phone
    db.commit()
    db.refresh(campus)
    return campus


@router.delete("/{campus_id}")
async def delete_campus(
    campus_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_admin_or_above)
):
    campus = db.query(Campus).filter(Campus.id == campus_id, Campus.is_deleted == False).first()
    if not campus:
        raise HTTPException(status_code=404, detail="Campus not found")
    campus.is_deleted = True
    db.commit()
    return {"message": "Campus deleted"}
