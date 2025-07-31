from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from app.crud.base import CRUDBase
from app.models.employment import Employment, EmploymentStatus
from app.schemas.employment import EmploymentCreate, EmploymentUpdate


class CRUDEmployment(CRUDBase[Employment, EmploymentCreate, EmploymentUpdate]):
    def create_with_employee(
        self, db: Session, *, obj_in: EmploymentCreate, employee_id: int
    ) -> Employment:
        obj_in_data = obj_in.dict()
        db_obj = Employment(**obj_in_data, employee_id=employee_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_by_employee(
        self, db: Session, *, employee_id: int, skip: int = 0, limit: int = 100
    ) -> List[Employment]:
        return (
            db.query(self.model)
            .filter(Employment.employee_id == employee_id)
            .order_by(Employment.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_current_employment(
        self, db: Session, *, employee_id: int
    ) -> Optional[Employment]:
        return (
            db.query(self.model)
            .filter(
                Employment.employee_id == employee_id,
                Employment.employment_status == EmploymentStatus.CURRENT
            )
            .first()
        )

    def set_as_current(
        self, db: Session, *, employment_id: int, employee_id: int
    ) -> Employment:
        # First, mark all other employments as ended
        db.query(self.model).filter(
            Employment.employee_id == employee_id,
            Employment.id != employment_id
        ).update({
            Employment.employment_status: EmploymentStatus.ENDED,
            Employment.end_date: datetime.utcnow()
        })
        
        # Then mark the specified employment as current
        employment = db.query(self.model).filter(
            Employment.id == employment_id
        ).first()
        
        if employment:
            employment.employment_status = EmploymentStatus.CURRENT
            employment.end_date = None
            db.add(employment)
            db.commit()
            db.refresh(employment)
        
        return employment

    def end_employment(
        self, db: Session, *, employment_id: int, end_date: datetime = None
    ) -> Employment:
        employment = db.query(self.model).filter(
            Employment.id == employment_id
        ).first()
        
        if employment:
            employment.employment_status = EmploymentStatus.ENDED
            employment.end_date = end_date or datetime.utcnow()
            db.add(employment)
            db.commit()
            db.refresh(employment)
        
        return employment

    def get_by_company(
        self, db: Session, *, company_name: str, skip: int = 0, limit: int = 100
    ) -> List[Employment]:
        return (
            db.query(self.model)
            .filter(Employment.company_name.ilike(f"%{company_name}%"))
            .offset(skip)
            .limit(limit)
            .all()
        )


employment = CRUDEmployment(Employment)
