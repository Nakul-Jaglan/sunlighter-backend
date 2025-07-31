from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.db.session import get_db
from app.models.user import User, UserType
from app.schemas.employment import Employment, EmploymentCreate, EmploymentUpdate, EmploymentWithCodes
from app.crud import crud_employment

router = APIRouter()


@router.get("/", response_model=List[EmploymentWithCodes])
def read_employments(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """Get employments for current user"""
    if current_user.user_type != UserType.EMPLOYEE:
        raise HTTPException(
            status_code=403, 
            detail="Only employees can access employment records"
        )
    
    employments = crud_employment.get_multi_by_employee(
        db, employee_id=current_user.id, skip=skip, limit=limit
    )
    return employments


@router.post("/", response_model=Employment)
def create_employment(
    *,
    db: Session = Depends(get_db),
    employment_in: EmploymentCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Create new employment record"""
    if current_user.user_type != UserType.EMPLOYEE:
        raise HTTPException(
            status_code=403, 
            detail="Only employees can create employment records"
        )
    
    employment = crud_employment.create_with_employee(
        db, obj_in=employment_in, employee_id=current_user.id
    )
    return employment


@router.get("/{employment_id}", response_model=Employment)
def read_employment(
    *,
    db: Session = Depends(get_db),
    employment_id: int,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Get employment by ID"""
    employment = crud_employment.get(db, id=employment_id)
    if not employment:
        raise HTTPException(status_code=404, detail="Employment not found")
    
    # Check if user owns this employment record
    if employment.employee_id != current_user.id:
        raise HTTPException(
            status_code=403, 
            detail="Not enough permissions"
        )
    
    return employment


@router.put("/{employment_id}", response_model=Employment)
def update_employment(
    *,
    db: Session = Depends(get_db),
    employment_id: int,
    employment_in: EmploymentUpdate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Update employment record"""
    employment = crud_employment.get(db, id=employment_id)
    if not employment:
        raise HTTPException(status_code=404, detail="Employment not found")
    
    # Check if user owns this employment record
    if employment.employee_id != current_user.id:
        raise HTTPException(
            status_code=403, 
            detail="Not enough permissions"
        )
    
    employment = crud_employment.update(db, db_obj=employment, obj_in=employment_in)
    return employment


@router.delete("/{employment_id}")
def delete_employment(
    *,
    db: Session = Depends(get_db),
    employment_id: int,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Delete employment record"""
    employment = crud_employment.get(db, id=employment_id)
    if not employment:
        raise HTTPException(status_code=404, detail="Employment not found")
    
    # Check if user owns this employment record
    if employment.employee_id != current_user.id:
        raise HTTPException(
            status_code=403, 
            detail="Not enough permissions"
        )
    
    employment = crud_employment.remove(db, id=employment_id)
    return {"message": "Employment record deleted successfully"}


@router.post("/{employment_id}/set-current")
def set_current_employment(
    *,
    db: Session = Depends(get_db),
    employment_id: int,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Set employment as current job"""
    employment = crud_employment.get(db, id=employment_id)
    if not employment:
        raise HTTPException(status_code=404, detail="Employment not found")
    
    # Check if user owns this employment record
    if employment.employee_id != current_user.id:
        raise HTTPException(
            status_code=403, 
            detail="Not enough permissions"
        )
    
    crud_employment.set_as_current(db, employment_id=employment_id, employee_id=current_user.id)
    return {"message": "Employment set as current job"}
