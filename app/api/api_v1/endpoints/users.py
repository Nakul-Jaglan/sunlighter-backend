from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import User as UserSchema, UserUpdate
from app.crud import crud_user

router = APIRouter()


@router.get("/me", response_model=UserSchema)
def read_user_me(
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Get current user"""
    return current_user


@router.put("/me", response_model=UserSchema)
def update_user_me(
    *,
    db: Session = Depends(get_db),
    user_in: UserUpdate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Update current user"""
    user = crud_user.update(db, db_obj=current_user, obj_in=user_in)
    return user


@router.get("/{user_id}", response_model=UserSchema)
def read_user(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Get user by ID (limited info for privacy)"""
    user = crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Only return basic info for privacy
    return UserSchema(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        user_type=user.user_type,
        is_active=user.is_active,
        is_verified=user.is_verified,
        created_at=user.created_at,
        company_name=user.company_name if user.user_type == "employer" else None
    )


@router.delete("/me")
def delete_user_me(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Delete current user account"""
    crud_user.remove(db, id=current_user.id)
    return {"message": "User account deleted successfully"}
