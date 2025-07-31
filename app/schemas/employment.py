from typing import Optional
from pydantic import BaseModel
from datetime import datetime

from app.models.employment import EmploymentType, EmploymentStatus


class EmploymentBase(BaseModel):
    company_name: str
    job_title: str
    employment_type: EmploymentType
    start_date: datetime
    company_location: Optional[str] = None
    department: Optional[str] = None
    salary_range: Optional[str] = None
    job_description: Optional[str] = None
    manager_name: Optional[str] = None
    manager_email: Optional[str] = None


class EmploymentCreate(EmploymentBase):
    pass


class EmploymentUpdate(BaseModel):
    company_name: Optional[str] = None
    job_title: Optional[str] = None
    employment_type: Optional[EmploymentType] = None
    employment_status: Optional[EmploymentStatus] = None
    end_date: Optional[datetime] = None
    company_location: Optional[str] = None
    department: Optional[str] = None
    salary_range: Optional[str] = None
    job_description: Optional[str] = None
    manager_name: Optional[str] = None
    manager_email: Optional[str] = None


class EmploymentInDB(EmploymentBase):
    id: int
    employee_id: int
    employment_status: EmploymentStatus
    end_date: Optional[datetime] = None
    is_verified: bool
    verification_method: Optional[str] = None
    verification_date: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class Employment(EmploymentInDB):
    pass


class EmploymentWithCodes(Employment):
    verification_codes_count: int = 0
