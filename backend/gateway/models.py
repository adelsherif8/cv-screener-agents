from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

try:
    from .database import Base
except ImportError:
    from database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # User profile information
    company_name = Column(String, nullable=True)
    job_title = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    bio = Column(Text, nullable=True)
    location = Column(String, nullable=True)
    
    # Relationship to jobs
    jobs = relationship("Job", back_populates="user")

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    requirements = Column(JSON, nullable=True)
    seniority = Column(String, nullable=True)
    domain_tags = Column(JSON, nullable=True)
    screening_questions = Column(JSON, nullable=True)
    ats_keywords = Column(JSON, nullable=True)
    summary = Column(Text, nullable=True)
    
    # User association
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="jobs")
    
    # Job metadata
    status = Column(String, default="draft")  # draft, published, paused, closed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    published_at = Column(DateTime(timezone=True), nullable=True)
    
    # Job posting details
    location = Column(String, nullable=True)
    remote_allowed = Column(Boolean, default=False)
    salary_min = Column(Integer, nullable=True)
    salary_max = Column(Integer, nullable=True)
    salary_currency = Column(String, default="USD")
    employment_type = Column(String, default="full-time")  # full-time, part-time, contract, internship
    application_deadline = Column(DateTime(timezone=True), nullable=True)
    
    # Analytics
    view_count = Column(Integer, default=0)
    application_count = Column(Integer, default=0)
