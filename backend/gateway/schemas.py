from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime

# User schemas
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None
    company_name: Optional[str] = None
    job_title: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserProfile(BaseModel):
    full_name: Optional[str] = None
    company_name: Optional[str] = None
    job_title: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    avatar_url: Optional[str] = None

class UserRead(BaseModel):
    id: int
    email: str
    username: str
    full_name: Optional[str] = None
    company_name: Optional[str] = None
    job_title: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserRead

# Updated Job schemas to include user association
class JobCreate(BaseModel):
    title: str
    description: str
    requirements: Optional[List[Dict[str, str]]] = []
    seniority: Optional[str] = None
    domain_tags: Optional[List[str]] = []
    screening_questions: Optional[List[str]] = []
    ats_keywords: Optional[List[str]] = []
    summary: Optional[str] = None
    location: Optional[str] = None
    remote_allowed: Optional[bool] = False
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: Optional[str] = "USD"
    employment_type: Optional[str] = "full-time"
    status: Optional[str] = "draft"

class JobUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[List[Dict[str, str]]] = None
    seniority: Optional[str] = None
    domain_tags: Optional[List[str]] = None
    screening_questions: Optional[List[str]] = None
    ats_keywords: Optional[List[str]] = None
    summary: Optional[str] = None
    location: Optional[str] = None
    remote_allowed: Optional[bool] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: Optional[str] = None
    employment_type: Optional[str] = None
    status: Optional[str] = None

class JobRead(JobCreate):
    id: int
    user_id: int
    user: UserRead
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    view_count: int
    application_count: int
    
    class Config:
        from_attributes = True

class JobSummary(BaseModel):
    id: int
    title: str
    location: Optional[str] = None
    status: str
    created_at: datetime
    view_count: int
    application_count: int
    
    class Config:
        from_attributes = True

class Skill(BaseModel):
    skill: str
    level: str

class SalarySuggestionRequest(BaseModel):
    job_title: str
    skills: List[Skill]
    location: str
    seniority_level: str  # Junior, Mid, Senior, Lead
    job_description: Optional[str] = ""
    company_size: Optional[str] = "medium"  # startup, small, medium, large, enterprise
    industry: Optional[str] = "technology"
    
class SalarySuggestionResponse(BaseModel):
    min_salary: int
    max_salary: int
    average_salary: int
    percentile_25: int
    percentile_75: int
    data_sources: List[str]
    confidence_score: float
    location_adjustment: float
    skill_premium: float
    seniority_multiplier: float
    market_trends: Dict[str, Any]
    comparable_positions: List[Dict[str, str]]

class ExperienceLevelRequest(BaseModel):
    job_title: str
    job_description: str
    requirements: Optional[str] = ""
    
class ExperienceLevelResponse(BaseModel):
    detected_level: str  # Entry, Junior, Mid, Senior, Lead, Executive
    confidence_score: float
    years_of_experience: Dict[str, Any]  # min, max, detected_ranges
    evidence: List[str]  # Text snippets that support the detection
    alternative_levels: List[Dict[str, Any]]  # Other possible levels with confidence
    recommendations: List[str]

class AutoCompleteRequest(BaseModel):
    context: str  # Current text being typed
    cursor_position: Optional[int] = None  # Position of cursor in text
    job_title: Optional[str] = ""  # Job title for context
    field_type: str  # "description", "requirements", "summary"
    
class AutoCompleteSuggestion(BaseModel):
    text: str  # The suggested text
    type: str  # "completion", "phrase", "bullet_point", "section"
    confidence: float  # How relevant this suggestion is
    category: str  # "responsibility", "requirement", "benefit", "culture"
    icon: Optional[str] = None  # Icon for the suggestion
    
class AutoCompleteResponse(BaseModel):
    suggestions: List[AutoCompleteSuggestion]
    context_detected: str  # What context was detected (tech, leadership, etc.)
    total_suggestions: int
