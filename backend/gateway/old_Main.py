from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import re
import json
import logging
import os
from pathlib import Path

# Conditional imports for running as module vs direct execution
try:
    from .db import SessionLocal, engine
    from .models import Base
    from .schemas import JobCreate, JobRead
    from .crud import create_job, get_jobs, get_job
except ImportError:
    # Running directly, not as module
    from db import SessionLocal, engine
    from models import Base
    from schemas import JobCreate, JobRead
    from crud import create_job, get_jobs, get_job

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="CV2 Gateway API", description="Gateway BFF for CV2 platform", version="1.0.0")

# Load skills taxonomy from JSON file
def load_skills_taxonomy() -> Dict[str, Any]:
    """Load skills taxonomy from external JSON file"""
    try:
        current_dir = Path(__file__).parent
        taxonomy_path = current_dir.parent / "skills_taxonomy.json"
        
        with open(taxonomy_path, 'r', encoding='utf-8') as f:
            taxonomy = json.load(f)
        
        logger.info(f"Loaded skills taxonomy with {taxonomy['metadata']['total_skills']} skills")
        return taxonomy
    except Exception as e:
        logger.error(f"Error loading skills taxonomy: {str(e)}")
        # Fallback to minimal taxonomy
        return {
            "core_skills": {
                "JavaScript": {"keywords": ["javascript", "js"], "category": "frontend", "weight": 0.9, "skill_type": "core"}
            },
            "soft_skills": {
                "Communication": {"keywords": ["communication"], "category": "interpersonal", "weight": 0.8, "skill_type": "soft"}
            },
            "bonus_skills": {
                "Git": {"keywords": ["git"], "category": "tools", "weight": 0.6, "skill_type": "bonus"}
            },
            "metadata": {"version": "fallback", "total_skills": 3}
        }

# Global taxonomy - loaded once at startup
SKILLS_TAXONOMY = load_skills_taxonomy()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables (use Alembic in production)
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Seed jobs for testing
@app.post("/jobs/seed")
def seed_jobs(db: Session = Depends(get_db)):
    """Seed database with test job data"""
    try:
        jobs_data = [
            {
                "title": "Product Manager",
                "description": "Lead product development and strategy for our growing tech platform.",
                "requirements": [{"skill": "Leadership", "level": "Expert", "weight": 0.9}],
                "seniority": "Lead",
                "domain_tags": ["management", "product"],
                "screening_questions": ["How do you prioritize product features?", "Describe your experience with agile methodologies."],
                "ats_keywords": ["Agile", "Scrum", "Leadership", "Product Strategy"],
                "summary": "Product Manager role for strategic leadership in a fast-growing tech company."
            },
            {
                "title": "Senior Frontend Developer",
                "description": "Develop and maintain modern React applications with TypeScript.",
                "requirements": [
                    {"skill": "React", "level": "Advanced", "weight": 0.9},
                    {"skill": "TypeScript", "level": "Advanced", "weight": 0.8}
                ],
                "seniority": "Senior",
                "domain_tags": ["engineering", "frontend"],
                "screening_questions": ["Describe your experience with React hooks.", "How do you handle state management?"],
                "ats_keywords": ["React", "TypeScript", "Frontend", "JavaScript"],
                "summary": "Senior Frontend Developer for modern web application development."
            }
        ]
        
        seeded = []
        for job_data in jobs_data:
            job = create_job(db, JobCreate(**job_data))
            seeded.append(job)
            logger.info(f"Seeded job: {job.title}")
        
        return {"message": f"Successfully seeded {len(seeded)} jobs", "jobs": seeded}
    
    except Exception as e:
        logger.error(f"Error seeding jobs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to seed jobs: {str(e)}")

# Enhanced AI Analysis Functions
# ...existing code...
# (Old main content preserved for reference; see active logic in main.py)
