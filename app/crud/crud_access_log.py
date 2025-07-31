from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from datetime import datetime

from app.crud.base import CRUDBase
from app.models.access_log import AccessLog
from app.models.verification_code import VerificationCode
from app.models.user import User
from app.schemas.access_log import AccessLogCreate, AccessLogUpdate


class CRUDAccessLog(CRUDBase[AccessLog, AccessLogCreate, AccessLogUpdate]):
    def get_multi_by_employee(
        self, db: Session, *, employee_id: int, skip: int = 0, limit: int = 100
    ) -> List[AccessLog]:
        return (
            db.query(self.model)
            .join(VerificationCode)
            .filter(VerificationCode.employee_id == employee_id)
            .order_by(AccessLog.accessed_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_multi_by_employer(
        self, db: Session, *, employer_id: int, skip: int = 0, limit: int = 100
    ) -> List[AccessLog]:
        return (
            db.query(self.model)
            .filter(AccessLog.employer_id == employer_id)
            .order_by(AccessLog.accessed_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_multi_by_verification_code(
        self, 
        db: Session, 
        *, 
        verification_code_id: int, 
        employee_id: int,
        skip: int = 0, 
        limit: int = 100
    ) -> List[AccessLog]:
        # Verify that the verification code belongs to the employee
        verification_code = (
            db.query(VerificationCode)
            .filter(
                VerificationCode.id == verification_code_id,
                VerificationCode.employee_id == employee_id
            )
            .first()
        )
        
        if not verification_code:
            return []
        
        return (
            db.query(self.model)
            .filter(AccessLog.verification_code_id == verification_code_id)
            .order_by(AccessLog.accessed_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_with_details(self, db: Session, *, id: int) -> Optional[AccessLog]:
        return (
            db.query(self.model)
            .options(joinedload(AccessLog.verification_code))
            .options(joinedload(AccessLog.employer))
            .filter(AccessLog.id == id)
            .first()
        )

    def get_pending_approvals(
        self, db: Session, *, employee_id: int, skip: int = 0, limit: int = 100
    ) -> List[AccessLog]:
        return (
            db.query(self.model)
            .join(VerificationCode)
            .filter(
                VerificationCode.employee_id == employee_id,
                AccessLog.requires_approval == True,
                AccessLog.approval_status == "pending"
            )
            .order_by(AccessLog.accessed_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def approve_request(
        self, db: Session, *, log_id: int, approver_id: int
    ) -> AccessLog:
        access_log = db.query(self.model).filter(AccessLog.id == log_id).first()
        
        if access_log:
            access_log.approval_status = "approved"
            access_log.approved_by = approver_id
            access_log.approved_at = datetime.utcnow()
            db.add(access_log)
            db.commit()
            db.refresh(access_log)
        
        return access_log

    def deny_request(
        self, db: Session, *, log_id: int, approver_id: int
    ) -> AccessLog:
        access_log = db.query(self.model).filter(AccessLog.id == log_id).first()
        
        if access_log:
            access_log.approval_status = "denied"
            access_log.approved_by = approver_id
            access_log.approved_at = datetime.utcnow()
            db.add(access_log)
            db.commit()
            db.refresh(access_log)
        
        return access_log

    def get_access_stats(
        self, db: Session, *, employee_id: int = None, employer_id: int = None
    ) -> dict:
        """Get access statistics for analytics"""
        query = db.query(self.model)
        
        if employee_id:
            query = query.join(VerificationCode).filter(
                VerificationCode.employee_id == employee_id
            )
        elif employer_id:
            query = query.filter(AccessLog.employer_id == employer_id)
        
        total_requests = query.count()
        successful_requests = query.filter(AccessLog.success == True).count()
        failed_requests = total_requests - successful_requests
        
        # Get recent activity (last 30 days)
        from datetime import timedelta
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_requests = query.filter(
            AccessLog.accessed_at >= thirty_days_ago
        ).count()
        
        return {
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "success_rate": (successful_requests / total_requests * 100) if total_requests > 0 else 0,
            "recent_requests": recent_requests
        }


access_log = CRUDAccessLog(AccessLog)
