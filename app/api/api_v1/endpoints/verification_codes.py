from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.api import deps
from app.db.session import get_db
from app.models.user import User, UserType
from app.schemas.verification_code import (
    VerificationCode, 
    VerificationCodeCreate, 
    VerificationCodeUpdate,
    VerificationRequest,
    VerificationResponse
)
from app.crud import crud_verification_code, crud_access_log

router = APIRouter()


@router.get("/", response_model=List[VerificationCode])
def read_verification_codes(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """Get verification codes for current user"""
    if current_user.user_type != UserType.EMPLOYEE:
        raise HTTPException(
            status_code=403, 
            detail="Only employees can access verification codes"
        )
    
    codes = crud_verification_code.get_multi_by_employee(
        db, employee_id=current_user.id, skip=skip, limit=limit
    )
    return codes


@router.post("/", response_model=VerificationCode)
def create_verification_code(
    *,
    db: Session = Depends(get_db),
    code_in: VerificationCodeCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Create new verification code"""
    if current_user.user_type != UserType.EMPLOYEE:
        raise HTTPException(
            status_code=403, 
            detail="Only employees can create verification codes"
        )
    
    code = crud_verification_code.create_with_employee(
        db, obj_in=code_in, employee_id=current_user.id
    )
    return code


@router.get("/{code_id}", response_model=VerificationCode)
def read_verification_code(
    *,
    db: Session = Depends(get_db),
    code_id: int,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Get verification code by ID"""
    code = crud_verification_code.get(db, id=code_id)
    if not code:
        raise HTTPException(status_code=404, detail="Verification code not found")
    
    # Check if user owns this code
    if code.employee_id != current_user.id:
        raise HTTPException(
            status_code=403, 
            detail="Not enough permissions"
        )
    
    return code


@router.put("/{code_id}", response_model=VerificationCode)
def update_verification_code(
    *,
    db: Session = Depends(get_db),
    code_id: int,
    code_in: VerificationCodeUpdate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Update verification code"""
    code = crud_verification_code.get(db, id=code_id)
    if not code:
        raise HTTPException(status_code=404, detail="Verification code not found")
    
    # Check if user owns this code
    if code.employee_id != current_user.id:
        raise HTTPException(
            status_code=403, 
            detail="Not enough permissions"
        )
    
    code = crud_verification_code.update(db, db_obj=code, obj_in=code_in)
    return code


@router.delete("/{code_id}")
def delete_verification_code(
    *,
    db: Session = Depends(get_db),
    code_id: int,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Delete verification code"""
    code = crud_verification_code.get(db, id=code_id)
    if not code:
        raise HTTPException(status_code=404, detail="Verification code not found")
    
    # Check if user owns this code
    if code.employee_id != current_user.id:
        raise HTTPException(
            status_code=403, 
            detail="Not enough permissions"
        )
    
    crud_verification_code.remove(db, id=code_id)
    return {"message": "Verification code deleted successfully"}


@router.post("/{code_id}/revoke")
def revoke_verification_code(
    *,
    db: Session = Depends(get_db),
    code_id: int,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Revoke verification code"""
    code = crud_verification_code.get(db, id=code_id)
    if not code:
        raise HTTPException(status_code=404, detail="Verification code not found")
    
    # Check if user owns this code
    if code.employee_id != current_user.id:
        raise HTTPException(
            status_code=403, 
            detail="Not enough permissions"
        )
    
    code = crud_verification_code.revoke(db, code=code)
    return {"message": "Verification code revoked successfully"}


@router.post("/verify", response_model=VerificationResponse)
def verify_employment(
    *,
    db: Session = Depends(get_db),
    request: Request,
    verification_request: VerificationRequest,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Verify employment using verification code"""
    if current_user.user_type != UserType.EMPLOYER:
        raise HTTPException(
            status_code=403, 
            detail="Only employers can verify employment"
        )
    
    # Get client IP and user agent for logging
    client_ip = request.client.host
    user_agent = request.headers.get("user-agent", "")
    
    result = crud_verification_code.verify_code(
        db, 
        code=verification_request.code,
        employer_id=current_user.id,
        ip_address=client_ip,
        user_agent=user_agent,
        request_purpose=verification_request.purpose
    )
    
    return result
