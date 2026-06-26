from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional

# Conditional imports for running as module vs direct execution
try:
    from .models import Job, User
    from .schemas import JobCreate, JobUpdate, UserCreate
    from .auth import get_password_hash
except ImportError:
    # Running directly, not as module
    from models import Job, User
    from schemas import JobCreate, JobUpdate, UserCreate
    from auth import get_password_hash

# User CRUD operations
def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email"""
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get user by username"""
    return db.query(User).filter(User.username == username).first()

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID"""
    return db.query(User).filter(User.id == user_id).first()

def create_user(db: Session, user: UserCreate) -> User:
    """Create a new user"""
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        full_name=user.full_name,
        company_name=user.company_name,
        job_title=user.job_title
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate user"""
    try:
        from .auth import verify_password
    except ImportError:
        from auth import verify_password
    
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

# Job CRUD operations
def create_job(db: Session, job: JobCreate, user_id: int) -> Job:
    """Create a new job for a user"""
    db_job = Job(
        title=job.title,
        description=job.description,
        requirements=job.requirements,
        seniority=job.seniority,
        domain_tags=job.domain_tags,
        screening_questions=job.screening_questions,
        ats_keywords=job.ats_keywords,
        summary=job.summary,
        location=job.location,
        remote_allowed=job.remote_allowed,
        salary_min=job.salary_min,
        salary_max=job.salary_max,
        salary_currency=job.salary_currency,
        employment_type=job.employment_type,
        status=job.status or "draft",
        user_id=user_id
    )
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job

def get_jobs(db: Session, skip: int = 0, limit: int = 100) -> List[Job]:
    """Get all jobs (for admin or public view)"""
    return db.query(Job).filter(Job.status == "published").offset(skip).limit(limit).all()

def get_user_jobs(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Job]:
    """Get all jobs for a specific user"""
    return db.query(Job).filter(Job.user_id == user_id).offset(skip).limit(limit).all()

def get_job(db: Session, job_id: int) -> Optional[Job]:
    """Get job by ID"""
    return db.query(Job).filter(Job.id == job_id).first()

def get_user_job(db: Session, job_id: int, user_id: int) -> Optional[Job]:
    """Get job by ID if it belongs to the user"""
    return db.query(Job).filter(and_(Job.id == job_id, Job.user_id == user_id)).first()

def update_job(db: Session, job_id: int, user_id: int, job_update: JobUpdate) -> Optional[Job]:
    """Update a job if it belongs to the user"""
    db_job = get_user_job(db, job_id, user_id)
    if not db_job:
        return None
    
    update_data = job_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_job, key, value)
    
    db.commit()
    db.refresh(db_job)
    return db_job

def delete_job(db: Session, job_id: int, user_id: int) -> bool:
    """Delete a job if it belongs to the user"""
    db_job = get_user_job(db, job_id, user_id)
    if not db_job:
        return False
    
    db.delete(db_job)
    db.commit()
    return True

def publish_job(db: Session, job_id: int, user_id: int) -> Optional[Job]:
    """Publish a job (change status to published)"""
    from datetime import datetime
    db_job = get_user_job(db, job_id, user_id)
    if not db_job:
        return None
    
    db_job.status = "published"
    db_job.published_at = datetime.utcnow()
    db.commit()
    db.refresh(db_job)
    return db_job
