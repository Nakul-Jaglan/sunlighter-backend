from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

from app.models.verification_code import VerificationCodeStatus


class VerificationCodeBase(BaseModel):
    purpose: str
    max_usage_count: int = 1
    expires_at: datetime
    require_approval: bool = False
    allowed_domains: Optional[str] = None


class VerificationCodeCreate(VerificationCodeBase):
    employment_id: int


class VerificationCodeUpdate(BaseModel):
    purpose: Optional[str] = None
    status: Optional[VerificationCodeStatus] = None
    max_usage_count: Optional[int] = None
    require_approval: Optional[bool] = None
    allowed_domains: Optional[str] = None


class VerificationCodeInDB(VerificationCodeBase):
    id: int
    code: str
    employee_id: int
    employment_id: int
    status: VerificationCodeStatus
    current_usage_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class VerificationCode(VerificationCodeInDB):
    pass


class VerificationCodeWithEmployment(VerificationCode):
    employment: dict  # Basic employment info


class VerificationRequest(BaseModel):
    code: str
    purpose: Optional[str] = None


class VerificationResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None
    employee_name: Optional[str] = None
    company_name: Optional[str] = None
    job_title: Optional[str] = None
    employment_status: Optional[str] = None
    verification_date: Optional[datetime] = None
