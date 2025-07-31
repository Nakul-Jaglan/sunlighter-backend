from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.session import Base


class AccessLog(Base):
    __tablename__ = "access_logs"

    id = Column(Integer, primary_key=True, index=True)
    verification_code_id = Column(Integer, ForeignKey("verification_codes.id"), nullable=False)
    employer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Access information
    accessed_at = Column(DateTime(timezone=True), server_default=func.now())
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    location = Column(String, nullable=True)  # Derived from IP
    
    # Request details
    request_purpose = Column(String, nullable=True)
    request_data = Column(JSON, nullable=True)  # Store any additional request data
    
    # Response details
    success = Column(Boolean, nullable=False)
    error_message = Column(Text, nullable=True)
    data_accessed = Column(JSON, nullable=True)  # What data was actually shared
    
    # Approval workflow
    requires_approval = Column(Boolean, default=False)
    approval_status = Column(String, nullable=True)  # "pending", "approved", "denied"
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    verification_code = relationship("VerificationCode", back_populates="access_logs")
    employer = relationship("User", back_populates="access_logs", foreign_keys=[employer_id])
    approver = relationship("User", foreign_keys=[approved_by])
