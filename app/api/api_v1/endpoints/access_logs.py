from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.db.session import get_db
from app.models.user import User, UserType
from app.schemas.access_log import AccessLog, AccessLogWithDetails
from app.crud import crud_access_log

router = APIRouter()


@router.get("/", response_model=List[AccessLogWithDetails])
def read_access_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """Get access logs for current user"""
    if current_user.user_type == UserType.EMPLOYEE:
        # Employees see logs of their employment verifications
        logs = crud_access_log.get_multi_by_employee(
            db, employee_id=current_user.id, skip=skip, limit=limit
        )
    elif current_user.user_type == UserType.EMPLOYER:
        # Employers see logs of their verification requests
        logs = crud_access_log.get_multi_by_employer(
            db, employer_id=current_user.id, skip=skip, limit=limit
        )
    else:
        raise HTTPException(status_code=403, detail="Invalid user type")
    
    return logs


@router.get("/{log_id}", response_model=AccessLogWithDetails)
def read_access_log(
    *,
    db: Session = Depends(get_db),
    log_id: int,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Get access log by ID"""
    log = crud_access_log.get_with_details(db, id=log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Access log not found")
    
    # Check permissions
    can_access = False
    if current_user.user_type == UserType.EMPLOYEE:
        # Check if this log is for the employee's verification code
        can_access = log.verification_code.employee_id == current_user.id
    elif current_user.user_type == UserType.EMPLOYER:
        # Check if this log is for the employer's request
        can_access = log.employer_id == current_user.id
    
    if not can_access:
        raise HTTPException(
            status_code=403, 
            detail="Not enough permissions"
        )
    
    return log


@router.get("/verification-code/{code_id}", response_model=List[AccessLogWithDetails])
def read_access_logs_by_code(
    *,
    db: Session = Depends(get_db),
    code_id: int,
    current_user: User = Depends(deps.get_current_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """Get access logs for a specific verification code"""
    # Only employees can see logs for their verification codes
    if current_user.user_type != UserType.EMPLOYEE:
        raise HTTPException(
            status_code=403, 
            detail="Only employees can access verification code logs"
        )
    
    logs = crud_access_log.get_multi_by_verification_code(
        db, 
        verification_code_id=code_id, 
        employee_id=current_user.id,
        skip=skip, 
        limit=limit
    )
    return logs


@router.post("/{log_id}/approve")
def approve_access_request(
    *,
    db: Session = Depends(get_db),
    log_id: int,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Approve an access request (for approval workflows)"""
    if current_user.user_type != UserType.EMPLOYEE:
        raise HTTPException(
            status_code=403, 
            detail="Only employees can approve access requests"
        )
    
    log = crud_access_log.get(db, id=log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Access log not found")
    
    # Check if this is the employee's verification code
    if log.verification_code.employee_id != current_user.id:
        raise HTTPException(
            status_code=403, 
            detail="Not enough permissions"
        )
    
    log = crud_access_log.approve_request(db, log_id=log_id, approver_id=current_user.id)
    return {"message": "Access request approved"}


@router.post("/{log_id}/deny")
def deny_access_request(
    *,
    db: Session = Depends(get_db),
    log_id: int,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Deny an access request (for approval workflows)"""
    if current_user.user_type != UserType.EMPLOYEE:
        raise HTTPException(
            status_code=403, 
            detail="Only employees can deny access requests"
        )
    
    log = crud_access_log.get(db, id=log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Access log not found")
    
    # Check if this is the employee's verification code
    if log.verification_code.employee_id != current_user.id:
        raise HTTPException(
            status_code=403, 
            detail="Not enough permissions"
        )
    
    log = crud_access_log.deny_request(db, log_id=log_id, approver_id=current_user.id)
    return {"message": "Access request denied"}
