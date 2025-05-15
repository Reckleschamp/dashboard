from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.api import deps
from app.core import auth, security

router = APIRouter()

@router.get("/me", response_model=schemas.User)
def get_current_user(
    current_user: models.User = Depends(auth.get_current_active_user),
):
    return current_user

@router.put("/me", response_model=schemas.User)
def update_user(
    user_in: schemas.UserUpdate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(auth.get_current_active_user),
):
    if user_in.name:
        current_user.name = user_in.name
    if user_in.email:
        current_user.email = user_in.email
    if user_in.password:
        current_user.hashed_password = security.get_password_hash(user_in.password)
    
    db.commit()
    db.refresh(current_user)
    return current_user

# Admin routes
@router.get("/", response_model=List[schemas.User])
def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(auth.get_current_admin_user),
):
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users

@router.get("/{user_id}", response_model=schemas.User)
def get_user_by_id(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(auth.get_current_admin_user),
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}/admin", response_model=schemas.User)
def set_admin_status(
    user_id: int,
    is_admin: bool,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(auth.get_current_admin_user),
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_admin = is_admin
    db.commit()
    db.refresh(user)
    return user