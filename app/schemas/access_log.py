from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class AccessLogBase(BaseModel):
    request_purpose: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    location: Optional[str] = None


class AccessLogCreate(AccessLogBase):
    verification_code_id: int
    success: bool
    error_message: Optional[str] = None
    data_accessed: Optional[dict] = None


class AccessLogUpdate(BaseModel):
    approval_status: Optional[str] = None
    approved_by: Optional[int] = None


class AccessLogInDB(AccessLogBase):
    id: int
    verification_code_id: int
    employer_id: int
    accessed_at: datetime
    success: bool
    error_message: Optional[str] = None
    data_accessed: Optional[dict] = None
    requires_approval: bool
    approval_status: Optional[str] = None
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        orm_mode = True


class AccessLog(AccessLogInDB):
    pass


class AccessLogWithDetails(AccessLog):
    employer_name: Optional[str] = None
    employer_company: Optional[str] = None
    verification_code: str
    employee_name: str
