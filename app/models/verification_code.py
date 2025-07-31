from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.db.session import Base


class VerificationCodeStatus(str, enum.Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    USED = "used"


class VerificationCode(Base):
    __tablename__ = "verification_codes"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True, nullable=False)
    employee_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    employment_id = Column(Integer, ForeignKey("employments.id"), nullable=False)
    
    # Code settings
    purpose = Column(String, nullable=False)  # e.g., "Job application at Google"
    status = Column(Enum(VerificationCodeStatus), default=VerificationCodeStatus.ACTIVE)
    max_usage_count = Column(Integer, default=1)
    current_usage_count = Column(Integer, default=0)
    
    # Expiry settings
    expires_at = Column(DateTime(timezone=True), nullable=False)
    
    # Access control
    require_approval = Column(Boolean, default=False)
    allowed_domains = Column(String, nullable=True)  # Comma-separated list
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    employee = relationship("User", back_populates="verification_codes")
    employment = relationship("Employment", back_populates="verification_codes")
    access_logs = relationship("AccessLog", back_populates="verification_code")
