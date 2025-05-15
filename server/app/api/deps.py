from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/login")

def get_db_session():
    return Depends(get_db)