from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.db.session import Base


class UserType(str, enum.Enum):
    EMPLOYEE = "employee"
    EMPLOYER = "employer"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True, nullable=True)  # Public alphanumeric ID for employees
    company_handle = Column(String, unique=True, index=True, nullable=True)  # Public handle for employers (@company)
    employer_id = Column(Integer, unique=True, index=True, nullable=True)  # Internal numeric ID for employers (100000-999999)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    user_type = Column(Enum(UserType), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Profile information
    phone_number = Column(String, nullable=True)
    profile_picture = Column(String, nullable=True)
    bio = Column(Text, nullable=True)
    location = Column(String, nullable=True)
    
    # Company information (for employers)
    company_name = Column(String, nullable=True)
    company_website = Column(String, nullable=True)
    company_size = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    employments = relationship("Employment", back_populates="employee", cascade="all, delete-orphan")
    verification_codes = relationship("VerificationCode", back_populates="employee", cascade="all, delete-orphan")
    access_logs = relationship("AccessLog", back_populates="employer", foreign_keys="AccessLog.employer_id")
