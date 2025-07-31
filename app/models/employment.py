from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.db.session import Base


class EmploymentType(str, enum.Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    FREELANCE = "freelance"
    INTERNSHIP = "internship"


class EmploymentStatus(str, enum.Enum):
    CURRENT = "current"
    ENDED = "ended"
    ON_LEAVE = "on_leave"


class Employment(Base):
    __tablename__ = "employments"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Company information
    company_name = Column(String, nullable=False)
    company_website = Column(String, nullable=True)
    company_location = Column(String, nullable=True)
    
    # Job information
    job_title = Column(String, nullable=False)
    department = Column(String, nullable=True)
    employment_type = Column(Enum(EmploymentType), nullable=False)
    employment_status = Column(Enum(EmploymentStatus), default=EmploymentStatus.CURRENT)
    
    # Dates
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=True)
    
    # Additional information
    salary_range = Column(String, nullable=True)
    benefits = Column(Text, nullable=True)
    job_description = Column(Text, nullable=True)
    manager_name = Column(String, nullable=True)
    manager_email = Column(String, nullable=True)
    
    # Verification information
    is_verified = Column(Boolean, default=False)
    verification_method = Column(String, nullable=True)  # e.g., "hr_email", "document_upload"
    verification_date = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    employee = relationship("User", back_populates="employments")
    verification_codes = relationship("VerificationCode", back_populates="employment")
