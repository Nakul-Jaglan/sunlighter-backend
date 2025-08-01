from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.core import security
from app.core.config import settings
from app.db.session import get_db
from app.models.user import User
from app.crud import crud_user

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)


def get_current_user(
    db: Session = Depends(get_db), 
    token: str = Depends(oauth2_scheme)
) -> User:
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = crud_user.get(db, id=int(user_id))
    if user is None:
        raise credentials_exception
    
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_current_employee(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Get current user if they are an employee"""
    if current_user.user_type != "employee":
        raise HTTPException(
            status_code=400, detail="The user must be an employee"
        )
    return current_user


def get_current_employer(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Get current user if they are an employer"""
    if current_user.user_type != "employer":
        raise HTTPException(
            status_code=400, detail="The user must be an employer"
        )
    return current_user
