from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from datetime import datetime

from app.crud.base import CRUDBase
from app.core.security import create_verification_code
from app.models.verification_code import VerificationCode, VerificationCodeStatus
from app.models.employment import Employment
from app.models.user import User
from app.models.access_log import AccessLog
from app.schemas.verification_code import VerificationCodeCreate, VerificationCodeUpdate, VerificationResponse


class CRUDVerificationCode(CRUDBase[VerificationCode, VerificationCodeCreate, VerificationCodeUpdate]):
    def create_with_employee(
        self, db: Session, *, obj_in: VerificationCodeCreate, employee_id: int
    ) -> VerificationCode:
        # Generate unique verification code
        code = create_verification_code()
        
        # Ensure uniqueness
        while db.query(VerificationCode).filter(VerificationCode.code == code).first():
            code = create_verification_code()
        
        obj_in_data = obj_in.dict()
        db_obj = VerificationCode(
            **obj_in_data,
            employee_id=employee_id,
            code=code
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_by_employee(
        self, db: Session, *, employee_id: int, skip: int = 0, limit: int = 100
    ) -> List[VerificationCode]:
        return (
            db.query(self.model)
            .filter(VerificationCode.employee_id == employee_id)
            .order_by(VerificationCode.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_code(self, db: Session, *, code: str) -> Optional[VerificationCode]:
        return (
            db.query(self.model)
            .options(joinedload(VerificationCode.employment))
            .options(joinedload(VerificationCode.employee))
            .filter(VerificationCode.code == code)
            .first()
        )

    def get_active_codes(
        self, db: Session, *, employee_id: int
    ) -> List[VerificationCode]:
        return (
            db.query(self.model)
            .filter(
                VerificationCode.employee_id == employee_id,
                VerificationCode.status == VerificationCodeStatus.ACTIVE,
                VerificationCode.expires_at > datetime.utcnow()
            )
            .all()
        )

    def revoke(self, db: Session, *, code: VerificationCode) -> VerificationCode:
        code.status = VerificationCodeStatus.REVOKED
        db.add(code)
        db.commit()
        db.refresh(code)
        return code

    def expire_old_codes(self, db: Session) -> int:
        """Expire codes that have passed their expiry time"""
        expired_count = (
            db.query(self.model)
            .filter(
                VerificationCode.status == VerificationCodeStatus.ACTIVE,
                VerificationCode.expires_at <= datetime.utcnow()
            )
            .update({VerificationCode.status: VerificationCodeStatus.EXPIRED})
        )
        db.commit()
        return expired_count

    def verify_code(
        self, 
        db: Session, 
        *, 
        code: str, 
        employer_id: int,
        ip_address: str = None,
        user_agent: str = None,
        request_purpose: str = None
    ) -> VerificationResponse:
        """Verify a verification code and log the access"""
        
        # Get the verification code
        verification_code = self.get_by_code(db, code=code)
        
        if not verification_code:
            # Log failed attempt
            self._log_access_attempt(
                db,
                verification_code_id=None,
                employer_id=employer_id,
                success=False,
                error_message="Invalid verification code",
                ip_address=ip_address,
                user_agent=user_agent,
                request_purpose=request_purpose
            )
            return VerificationResponse(
                success=False,
                message="Invalid verification code"
            )
        
        # Check if code is active
        if verification_code.status != VerificationCodeStatus.ACTIVE:
            self._log_access_attempt(
                db,
                verification_code_id=verification_code.id,
                employer_id=employer_id,
                success=False,
                error_message=f"Code is {verification_code.status.value}",
                ip_address=ip_address,
                user_agent=user_agent,
                request_purpose=request_purpose
            )
            return VerificationResponse(
                success=False,
                message=f"Verification code is {verification_code.status.value}"
            )
        
        # Check if code has expired
        if verification_code.expires_at <= datetime.utcnow():
            verification_code.status = VerificationCodeStatus.EXPIRED
            db.add(verification_code)
            db.commit()
            
            self._log_access_attempt(
                db,
                verification_code_id=verification_code.id,
                employer_id=employer_id,
                success=False,
                error_message="Code has expired",
                ip_address=ip_address,
                user_agent=user_agent,
                request_purpose=request_purpose
            )
            return VerificationResponse(
                success=False,
                message="Verification code has expired"
            )
        
        # Check usage count
        if verification_code.current_usage_count >= verification_code.max_usage_count:
            self._log_access_attempt(
                db,
                verification_code_id=verification_code.id,
                employer_id=employer_id,
                success=False,
                error_message="Code usage limit exceeded",
                ip_address=ip_address,
                user_agent=user_agent,
                request_purpose=request_purpose
            )
            return VerificationResponse(
                success=False,
                message="Verification code usage limit exceeded"
            )
        
        # Code is valid, increment usage count
        verification_code.current_usage_count += 1
        verification_code.last_used_at = datetime.utcnow()
        
        # If max usage reached, mark as used
        if verification_code.current_usage_count >= verification_code.max_usage_count:
            verification_code.status = VerificationCodeStatus.USED
        
        db.add(verification_code)
        
        # Prepare response data
        employment = verification_code.employment
        employee = verification_code.employee
        
        response_data = {
            "employment_id": employment.id,
            "company_name": employment.company_name,
            "job_title": employment.job_title,
            "employment_type": employment.employment_type.value,
            "employment_status": employment.employment_status.value,
            "start_date": employment.start_date.isoformat(),
            "end_date": employment.end_date.isoformat() if employment.end_date else None,
            "department": employment.department,
            "location": employment.company_location,
            "is_verified": employment.is_verified,
            "verification_date": employment.verification_date.isoformat() if employment.verification_date else None
        }
        
        # Log successful access
        self._log_access_attempt(
            db,
            verification_code_id=verification_code.id,
            employer_id=employer_id,
            success=True,
            data_accessed=response_data,
            ip_address=ip_address,
            user_agent=user_agent,
            request_purpose=request_purpose
        )
        
        db.commit()
        
        return VerificationResponse(
            success=True,
            message="Employment verification successful",
            data=response_data,
            employee_name=employee.full_name,
            company_name=employment.company_name,
            job_title=employment.job_title,
            employment_status=employment.employment_status.value,
            verification_date=datetime.utcnow()
        )
    
    def _log_access_attempt(
        self,
        db: Session,
        *,
        verification_code_id: Optional[int],
        employer_id: int,
        success: bool,
        error_message: str = None,
        data_accessed: dict = None,
        ip_address: str = None,
        user_agent: str = None,
        request_purpose: str = None
    ):
        """Log an access attempt"""
        access_log = AccessLog(
            verification_code_id=verification_code_id,
            employer_id=employer_id,
            success=success,
            error_message=error_message,
            data_accessed=data_accessed,
            ip_address=ip_address,
            user_agent=user_agent,
            request_purpose=request_purpose
        )
        db.add(access_log)


verification_code = CRUDVerificationCode(VerificationCode)
