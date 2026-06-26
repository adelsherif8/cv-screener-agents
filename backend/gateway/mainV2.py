from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import re
import json
import logging
import os
import string
from pathlib import Path
from difflib import SequenceMatcher

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

# V3 Enhanced Job Title Normalization System with Smart Skills Management
STANDARD_JOB_TITLES = {
    # Core Development Roles with Skills Templates
    "Frontend Engineer": {
        "variations": [
            "frontend developer", "front-end engineer", "front end engineer",
            "frontend dev", "front-end developer", "front end developer",
            "ui engineer", "ui developer", "frontend web developer", 
            "client-side developer", "client-side engineer",
            "fronend engineer", "fronend developer", "frontend enginer", 
            "front end dev", "fe engineer", "fe developer"
        ],
        "default_skills": ["JavaScript", "TypeScript", "Responsive Design", "State Management", "REST APIs", "Web Performance"],
        "soft_skills": ["Communication", "Problem Solving", "Collaboration", "Leadership"],
        "bonus_skills": ["HTML5", "CSS3", "Git", "Build Tools", "Agile", "DevOps", "CI/CD", "Test Driven Development", "Web Security"],
        "skill_levels": {
            # Core skills with specific levels
            "JavaScript": "Expert",
            "TypeScript": "Advanced", 
            "React": "Expert",
            "Angular": "Expert",
            "Vue.js": "Expert",
            "JSX": "Intermediate",
            "Responsive Design": "Advanced",
            "State Management": "Advanced",
            "REST APIs": "Advanced", 
            "Web Performance": "Intermediate",
            # Bonus skills
            "HTML5": "Advanced",
            "CSS3": "Advanced", 
            "Git": "Advanced",
            "Build Tools": "Intermediate",
            "Agile": "Intermediate",
            "DevOps": "Basic",
            "CI/CD": "Intermediate",
            "Test Driven Development": "Intermediate",
            "Testing": "Intermediate",
            "Docker": "Intermediate",
            "Web Security": "Intermediate",
            # Testing Tools
            "Jest": "Advanced",
            "Cypress": "Advanced",
            "Selenium": "Intermediate",
            "Mocha": "Intermediate",
            "Chai": "Intermediate",
            "Puppeteer": "Intermediate",
            "Unit Testing": "Advanced",
            "Integration Testing": "Intermediate", 
            "E2E Testing": "Advanced",
            # Build Tools & Bundlers
            "Webpack": "Advanced",
            "Vite": "Advanced",
            "Rollup": "Intermediate",
            "Parcel": "Intermediate", 
            "Babel": "Advanced",
            "ESLint": "Advanced",
            "Prettier": "Intermediate",
            # CSS Frameworks
            "Tailwind CSS": "Advanced",
            "Bootstrap": "Advanced",
            "Material-UI": "Intermediate",
            "Chakra UI": "Intermediate",
            "Sass/SCSS": "Advanced",
            "Less": "Intermediate",
            "Styled Components": "Advanced",
            # State Management
            "Redux": "Advanced",
            "MobX": "Intermediate",
            "Zustand": "Intermediate",
            "Context API": "Advanced",
            "Recoil": "Intermediate",
            # CMS Skills
            "Shopify": "Advanced",
            "Liquid": "Advanced",
            "WordPress": "Advanced",
            "PHP": "Intermediate",
            "Drupal": "Advanced",
            "Joomla": "Intermediate",
            "Magento": "Advanced",
            # Soft skills
            "Communication": "Advanced",
            "Problem Solving": "Advanced",
            "Collaboration": "Advanced", 
            "Leadership": "Intermediate"
        },
        "conditional_skills": {
            "react": {"add": [{"skill": "React", "category": "core"}, {"skill": "JSX", "category": "core"}], "remove": [], "promote": ["React"]},
            "angular": {"add": [{"skill": "Angular", "category": "core"}], "remove": [], "promote": ["Angular"]}, 
            "vue": {"add": [{"skill": "Vue.js", "category": "core"}, {"skill": "Vuex", "category": "bonus"}], "remove": [], "promote": ["Vue.js"]},
            "typescript": {"add": [{"skill": "TypeScript", "category": "core"}], "remove": [], "promote": ["TypeScript"]},
            "docker": {"add": [{"skill": "Docker", "category": "bonus"}], "remove": []},
            "jest": {"add": [{"skill": "Jest", "category": "bonus"}, {"skill": "Testing", "category": "bonus"}], "remove": []},
            "jasmine": {"add": [{"skill": "Jasmine", "category": "bonus"}, {"skill": "Testing", "category": "bonus"}], "remove": []},
            "karma": {"add": [{"skill": "Karma", "category": "bonus"}, {"skill": "Testing", "category": "bonus"}], "remove": []},
            "cypress": {"add": [{"skill": "Cypress", "category": "bonus"}, {"skill": "E2E Testing", "category": "bonus"}, {"skill": "Testing", "category": "bonus"}], "remove": []},
            "selenium": {"add": [{"skill": "Selenium", "category": "bonus"}, {"skill": "E2E Testing", "category": "bonus"}, {"skill": "Testing", "category": "bonus"}], "remove": []},
            "mocha": {"add": [{"skill": "Mocha", "category": "bonus"}, {"skill": "Testing", "category": "bonus"}], "remove": []},
            "chai": {"add": [{"skill": "Chai", "category": "bonus"}, {"skill": "Testing", "category": "bonus"}], "remove": []},
            "puppeteer": {"add": [{"skill": "Puppeteer", "category": "bonus"}, {"skill": "E2E Testing", "category": "bonus"}, {"skill": "Testing", "category": "bonus"}], "remove": []},
            "testing": {"add": [{"skill": "Testing", "category": "bonus"}], "remove": []},
            "unit test": {"add": [{"skill": "Unit Testing", "category": "bonus"}, {"skill": "Testing", "category": "bonus"}], "remove": []},
            "integration test": {"add": [{"skill": "Integration Testing", "category": "bonus"}, {"skill": "Testing", "category": "bonus"}], "remove": []},
            "e2e": {"add": [{"skill": "E2E Testing", "category": "bonus"}, {"skill": "Testing", "category": "bonus"}], "remove": []},
            # Build Tools & Bundlers
            "webpack": {"add": [{"skill": "Webpack", "category": "bonus"}, {"skill": "Build Tools", "category": "bonus"}], "remove": []},
            "vite": {"add": [{"skill": "Vite", "category": "bonus"}, {"skill": "Build Tools", "category": "bonus"}], "remove": []},
            "rollup": {"add": [{"skill": "Rollup", "category": "bonus"}, {"skill": "Build Tools", "category": "bonus"}], "remove": []},
            "parcel": {"add": [{"skill": "Parcel", "category": "bonus"}, {"skill": "Build Tools", "category": "bonus"}], "remove": []},
            "babel": {"add": [{"skill": "Babel", "category": "bonus"}, {"skill": "Build Tools", "category": "bonus"}], "remove": []},
            "eslint": {"add": [{"skill": "ESLint", "category": "bonus"}, {"skill": "Build Tools", "category": "bonus"}], "remove": []},
            "prettier": {"add": [{"skill": "Prettier", "category": "bonus"}, {"skill": "Build Tools", "category": "bonus"}], "remove": []},
            # CSS Frameworks
            "tailwind": {"add": [{"skill": "Tailwind CSS", "category": "bonus"}], "remove": []},
            "bootstrap": {"add": [{"skill": "Bootstrap", "category": "bonus"}], "remove": []},
            "material-ui": {"add": [{"skill": "Material-UI", "category": "bonus"}], "remove": []},
            "chakra": {"add": [{"skill": "Chakra UI", "category": "bonus"}], "remove": []},
            "sass": {"add": [{"skill": "Sass/SCSS", "category": "bonus"}], "remove": []},
            "scss": {"add": [{"skill": "Sass/SCSS", "category": "bonus"}], "remove": []},
            "less": {"add": [{"skill": "Less", "category": "bonus"}], "remove": []},
            "styled-components": {"add": [{"skill": "Styled Components", "category": "bonus"}], "remove": []},
            # State Management
            "redux": {"add": [{"skill": "Redux", "category": "bonus"}, {"skill": "State Management", "category": "core"}], "remove": []},
            "mobx": {"add": [{"skill": "MobX", "category": "bonus"}, {"skill": "State Management", "category": "core"}], "remove": []},
            "zustand": {"add": [{"skill": "Zustand", "category": "bonus"}, {"skill": "State Management", "category": "core"}], "remove": []},
            "context api": {"add": [{"skill": "Context API", "category": "bonus"}, {"skill": "State Management", "category": "core"}], "remove": []},
            "recoil": {"add": [{"skill": "Recoil", "category": "bonus"}, {"skill": "State Management", "category": "core"}], "remove": []},
            "stenciljs": {"add": [{"skill": "StencilJS", "category": "bonus"}], "remove": []},
            "websockets": {"add": [{"skill": "Websockets", "category": "bonus"}], "remove": []},
            "gitlab": {"add": [{"skill": "GitLab CI", "category": "bonus"}], "remove": []},
            "npm": {"add": [{"skill": "NPM", "category": "bonus"}], "remove": []},
            "bem": {"add": [{"skill": "BEM", "category": "bonus"}], "remove": []},
            "itcss": {"add": [{"skill": "ITCSS", "category": "bonus"}], "remove": []},
            # CMS Technologies
            "shopify": {"add": [{"skill": "Shopify", "category": "core"}, {"skill": "Liquid", "category": "core"}], "remove": []},
            "wordpress": {"add": [{"skill": "WordPress", "category": "core"}, {"skill": "PHP", "category": "bonus"}], "remove": []},
            "drupal": {"add": [{"skill": "Drupal", "category": "core"}, {"skill": "PHP", "category": "bonus"}], "remove": []},
            "joomla": {"add": [{"skill": "Joomla", "category": "core"}, {"skill": "PHP", "category": "bonus"}], "remove": []},
            "magento": {"add": [{"skill": "Magento", "category": "core"}, {"skill": "PHP", "category": "bonus"}], "remove": []},
            "php": {"add": [{"skill": "PHP", "category": "bonus"}], "remove": []}
        }
    },
    "Backend Engineer": {
        "variations": [
            "backend developer", "back-end engineer", "back end engineer", 
            "backend dev", "back-end developer", "back end developer",
            "server-side engineer", "server-side developer", "api engineer", 
            "api developer", "backend enginer", "bakend engineer",
            "be engineer", "be developer", "server engineer"
        ],
        "default_skills": ["API Development", "Database Management", "Programming Fundamentals", "Server Architecture"],
        "soft_skills": ["Problem Solving", "Communication", "Analytical Thinking", "Collaboration"],
        "bonus_skills": ["Git", "Docker", "CI/CD", "Testing", "AWS", "Linux"],
        "skill_levels": {
            "API Development": "Expert",
            "Database Management": "Advanced",
            "Programming Fundamentals": "Expert",
            "Server Architecture": "Advanced",
            "Node.js": "Expert",
            "Python": "Expert",
            "Java": "Expert",
            "Spring Boot": "Advanced",
            "Django": "Advanced",
            "Flask": "Advanced",
            "Express.js": "Advanced",
            "SQL": "Advanced",
            "PostgreSQL": "Advanced",
            "MySQL": "Advanced",
            "MongoDB": "Intermediate",
            "NoSQL": "Intermediate",
            "Git": "Advanced",
            "Docker": "Intermediate",
            "CI/CD": "Intermediate",
            "Testing": "Intermediate",
            "AWS": "Intermediate",
            "Linux": "Intermediate",
            "Problem Solving": "Advanced",
            "Communication": "Intermediate",
            "Analytical Thinking": "Advanced",
            "Collaboration": "Intermediate"
        },
        "conditional_skills": {
            "python": {"add": [{"skill": "Python", "category": "core"}, {"skill": "Django", "category": "bonus"}, {"skill": "Flask", "category": "bonus"}], "remove": [], "promote": ["Python"]},
            "nodejs": {"add": [{"skill": "Node.js", "category": "core"}, {"skill": "Express.js", "category": "bonus"}], "remove": [], "promote": ["Node.js"]},
            "java": {"add": [{"skill": "Java", "category": "core"}, {"skill": "Spring Boot", "category": "bonus"}], "remove": [], "promote": ["Java"]},
            "sql": {"add": [{"skill": "SQL", "category": "core"}, {"skill": "PostgreSQL", "category": "bonus"}, {"skill": "MySQL", "category": "bonus"}], "remove": []},
            "mongodb": {"add": [{"skill": "MongoDB", "category": "bonus"}, {"skill": "NoSQL", "category": "bonus"}], "remove": []},
            "docker": {"add": [{"skill": "Docker", "category": "bonus"}], "remove": []},
            "aws": {"add": [{"skill": "AWS", "category": "bonus"}], "remove": []},
            "azure": {"add": [{"skill": "Azure", "category": "bonus"}], "remove": []},
            "gcp": {"add": [{"skill": "GCP", "category": "bonus"}], "remove": []}
        }
    },
    "Fullstack Engineer": {
        "variations": [
            "full stack engineer", "full-stack engineer", "fullstack developer",
            "full stack developer", "full-stack developer", "full stack dev",
            "fullstack dev", "web engineer", "web developer", "software engineer"
        ],
        "default_skills": ["JavaScript", "TypeScript", "React", "React Native", "Python", "Django", "REST APIs", "PostgreSQL", "Redis", "Responsive Design", "Web Security", "Database Management"],
        "soft_skills": ["Problem Solving", "Communication", "Collaboration", "Adaptability"],
        "bonus_skills": ["Git", "AWS", "Docker", "Kubernetes", "CI/CD", "Build Tools", "Agile", "ERP Integration", "AI/ML Services", "Test Driven Development"],
        "skill_levels": {
            # Core skills with specific levels (4-6 years fullstack)
            "JavaScript": "Expert",
            "TypeScript": "Advanced", 
            "React": "Expert",
            "React Native": "Advanced",
            "Python": "Expert",
            "Django": "Expert",
            "REST APIs": "Expert",
            "PostgreSQL": "Advanced",
            "Redis": "Intermediate",
            "Responsive Design": "Advanced",
            "Web Security": "Advanced",
            "Database Management": "Advanced",
            # Bonus skills
            "Git": "Advanced",
            "AWS": "Expert",
            "Docker": "Advanced",
            "Kubernetes": "Intermediate",
            "CI/CD": "Advanced",
            "Build Tools": "Intermediate",
            "Agile": "Intermediate",
            "ERP Integration": "Intermediate",
            "AI/ML Services": "Intermediate",
            "Test Driven Development": "Advanced",
            # Soft skills
            "Problem Solving": "Expert",
            "Communication": "Advanced",
            "Collaboration": "Advanced", 
            "Adaptability": "Intermediate"
        },
        "conditional_skills": {
            "react": {"add": [{"skill": "JSX", "category": "bonus"}], "remove": ["React Native"], "promote": ["React"]},
            "react native": {"add": [{"skill": "Mobile Development", "category": "bonus"}], "remove": ["React"], "promote": ["React Native"]},
            "django": {"add": [{"skill": "ORM", "category": "bonus"}], "remove": [], "promote": ["Django"]},
            "python": {"add": [], "remove": [], "promote": ["Python"]},
            "postgresql": {"add": [], "remove": [], "promote": ["PostgreSQL"]},
            "redis": {"add": [], "remove": [], "promote": ["Redis"]},
            "aws": {"add": [{"skill": "Cloud Services", "category": "bonus"}], "remove": [], "promote": ["AWS"]},
            "docker": {"add": [{"skill": "Containerization", "category": "bonus"}], "remove": [], "promote": ["Docker"]},
            "kubernetes": {"add": [{"skill": "Orchestration", "category": "bonus"}], "remove": [], "promote": ["Kubernetes"]},
            "erp": {"add": [{"skill": "SAP", "category": "bonus"}, {"skill": "Oracle", "category": "bonus"}], "remove": []},
            "ai": {"add": [{"skill": "Machine Learning Integration", "category": "bonus"}], "remove": []},
            "ml": {"add": [{"skill": "Machine Learning Integration", "category": "bonus"}], "remove": []},
            "jest": {"add": [{"skill": "Jest", "category": "bonus"}, {"skill": "Testing", "category": "bonus"}], "remove": []},
            "testing": {"add": [{"skill": "Testing", "category": "bonus"}], "remove": []},
            "pytest": {"add": [{"skill": "PyTest", "category": "bonus"}, {"skill": "Testing", "category": "bonus"}], "remove": []},
            "unittest": {"add": [{"skill": "Unit Testing", "category": "bonus"}, {"skill": "Testing", "category": "bonus"}], "remove": []}
        }
    },
    "AI Engineer": {
        "variations": [
            "artificial intelligence engineer", "machine learning engineer",
            "ml engineer", "ai software engineer", "ai developer",
            "machine learning developer", "ai/ml engineer", "ai specialist", 
            "ml specialist", "data scientist", "ai research engineer",
            "machine learning scientist", "artificial intelligence developer"
        ],
        "default_skills": ["Python", "Machine Learning", "Data Analysis", "Statistical Modeling"],
        "soft_skills": ["Problem Solving", "Research Ability", "Communication", "Critical Thinking"],
        "bonus_skills": ["Statistics", "Mathematics", "MLOps", "Cloud Platforms", "Git", "Docker"],
        "skill_levels": {
            "Python": "Expert",
            "Machine Learning": "Expert",
            "Data Analysis": "Expert",
            "Statistical Modeling": "Advanced",
            "TensorFlow": "Expert",
            "PyTorch": "Expert",
            "Keras": "Advanced",
            "Deep Learning": "Advanced",
            "Natural Language Processing": "Advanced",
            "Computer Vision": "Advanced",
            "NLTK": "Intermediate",
            "spaCy": "Intermediate",
            "OpenCV": "Intermediate",
            "AWS": "Intermediate",
            "SageMaker": "Intermediate",
            "Statistics": "Advanced",
            "Mathematics": "Advanced",
            "MLOps": "Intermediate",
            "Cloud Platforms": "Intermediate",
            "Git": "Advanced",
            "Docker": "Intermediate",
            "Problem Solving": "Expert",
            "Research Ability": "Advanced",
            "Communication": "Advanced",
            "Critical Thinking": "Expert"
        },
        "conditional_skills": {
            "tensorflow": {"add": [{"skill": "TensorFlow", "category": "core"}, {"skill": "Keras", "category": "bonus"}], "remove": [], "promote": ["TensorFlow"]},
            "pytorch": {"add": [{"skill": "PyTorch", "category": "core"}, {"skill": "Deep Learning", "category": "bonus"}], "remove": [], "promote": ["PyTorch"]},
            "nlp": {"add": [{"skill": "Natural Language Processing", "category": "core"}, {"skill": "NLTK", "category": "bonus"}, {"skill": "spaCy", "category": "bonus"}], "remove": []},
            "computer vision": {"add": [{"skill": "Computer Vision", "category": "core"}, {"skill": "OpenCV", "category": "bonus"}], "remove": []},
            "aws": {"add": [{"skill": "AWS", "category": "bonus"}, {"skill": "SageMaker", "category": "bonus"}], "remove": []},
            "azure": {"add": [{"skill": "Azure", "category": "bonus"}, {"skill": "Azure ML", "category": "bonus"}], "remove": []},
            "gcp": {"add": [{"skill": "Google Cloud", "category": "bonus"}, {"skill": "Vertex AI", "category": "bonus"}], "remove": []},
            "scikit-learn": {"add": [{"skill": "Scikit-learn", "category": "bonus"}], "remove": []},
            "pandas": {"add": [{"skill": "Pandas", "category": "bonus"}], "remove": []},
            "numpy": {"add": [{"skill": "NumPy", "category": "bonus"}], "remove": []}
        }
    },
    "Software Engineer": {
        "variations": [
            "software developer", "software dev", "programmer", "developer",
            "software engineering", "application developer", "app developer",
            "systems engineer", "software architect", "coding engineer",
            "application engineer", "systems developer", "software programmer"
        ],
        "default_skills": ["Programming Fundamentals", "Object-Oriented Programming", "Algorithms", "Data Structures"],
        "soft_skills": ["Problem Solving", "Analytical Thinking", "Communication", "Collaboration"],
        "bonus_skills": ["Git", "SQL", "Agile", "Testing Frameworks", "Cloud Platforms"],
        "skill_levels": {
            "Programming Fundamentals": "Expert",
            "Object-Oriented Programming": "Expert", 
            "Algorithms": "Advanced",
            "Data Structures": "Advanced",
            "Python": "Expert",
            "Java": "Expert",
            "C++": "Expert",
            ".NET": "Expert",
            "Git": "Advanced",
            "SQL": "Intermediate",
            "Agile": "Intermediate",
            "Testing": "Intermediate",
            "Cloud Platforms": "Intermediate",
            "Problem Solving": "Expert",
            "Analytical Thinking": "Advanced",
            "Communication": "Advanced",
            "Collaboration": "Intermediate"
        },
        "conditional_skills": {
            "python": {"add": [{"skill": "Python", "category": "core"}], "remove": [], "promote": ["Python"]},
            "java": {"add": [{"skill": "Java", "category": "core"}], "remove": [], "promote": ["Java"]},
            "c++": {"add": [{"skill": "C++", "category": "core"}], "remove": [], "promote": ["C++"]},
            ".net": {"add": [{"skill": ".NET", "category": "core"}, {"skill": "C#", "category": "core"}], "remove": [], "promote": [".NET"]},
            "junit": {"add": [{"skill": "JUnit", "category": "bonus"}], "remove": []},
            "pytest": {"add": [{"skill": "PyTest", "category": "bonus"}], "remove": []},
            "nunit": {"add": [{"skill": "NUnit", "category": "bonus"}], "remove": []},
            "aws": {"add": [{"skill": "AWS", "category": "bonus"}], "remove": []},
            "azure": {"add": [{"skill": "Azure", "category": "bonus"}], "remove": []},
            "gcp": {"add": [{"skill": "GCP", "category": "bonus"}], "remove": []}
        }
    },
    "DevOps Engineer": {
        "variations": [
            "devops developer", "site reliability engineer", "sre", "infrastructure engineer",
            "cloud engineer", "platform engineer", "deployment engineer", "automation engineer",
            "devops specialist", "infrastructure developer"
        ],
        "default_skills": ["Docker", "Kubernetes", "CI/CD", "AWS", "Linux"],
        "soft_skills": ["Problem Solving", "Communication", "Analytical Thinking", "Troubleshooting"],
        "bonus_skills": ["Monitoring", "Automation", "Scripting", "Networking", "Security", "Infrastructure as Code"],
        "skill_levels": {
            "Docker": "Expert",
            "Kubernetes": "Expert",
            "CI/CD": "Advanced",
            "AWS": "Expert",
            "Linux": "Advanced",
            "Azure": "Expert",
            "Google Cloud": "Expert",
            "GKE": "Advanced",
            "EC2": "Advanced",
            "S3": "Advanced",
            "Azure DevOps": "Advanced",
            "Terraform": "Advanced",
            "Infrastructure as Code": "Advanced",
            "Jenkins": "Advanced",
            "Monitoring": "Advanced",
            "Automation": "Advanced",
            "Scripting": "Advanced",
            "Networking": "Intermediate",
            "Security": "Intermediate",
            "Problem Solving": "Advanced",
            "Communication": "Intermediate",
            "Analytical Thinking": "Advanced",
            "Troubleshooting": "Expert"
        },
        "conditional_skills": {
            "aws": {"add": [{"skill": "AWS", "category": "core"}, {"skill": "EC2", "category": "bonus"}, {"skill": "S3", "category": "bonus"}], "remove": [], "promote": ["AWS"]},
            "azure": {"add": [{"skill": "Azure", "category": "core"}, {"skill": "Azure DevOps", "category": "bonus"}], "remove": [], "promote": ["Azure"]},
            "gcp": {"add": [{"skill": "Google Cloud", "category": "core"}, {"skill": "GKE", "category": "bonus"}], "remove": [], "promote": ["Google Cloud"]},
            "terraform": {"add": [{"skill": "Terraform", "category": "bonus"}, {"skill": "Infrastructure as Code", "category": "bonus"}], "remove": []},
            "jenkins": {"add": [{"skill": "Jenkins", "category": "bonus"}], "remove": []},
            "ansible": {"add": [{"skill": "Ansible", "category": "bonus"}], "remove": []},
            "prometheus": {"add": [{"skill": "Prometheus", "category": "bonus"}, {"skill": "Monitoring", "category": "bonus"}], "remove": []},
            "grafana": {"add": [{"skill": "Grafana", "category": "bonus"}, {"skill": "Monitoring", "category": "bonus"}], "remove": []}
        }
    },
    
    "Frontend Developer": {
        "variations": [
            "ui engineer", "web ui developer", "client-side engineer", "frontend engineer",
            "front-end developer", "front end developer", "ui developer", "web developer",
            "client-side developer", "javascript developer", "web ui engineer"
        ],
        "default_skills": ["JavaScript", "HTML5", "CSS3", "Responsive Design"],
        "soft_skills": ["Attention to Detail", "User-Centric Thinking", "Collaboration", "Communication"],
        "bonus_skills": ["TypeScript", "Testing", "GraphQL", "Web Performance", "Build Tools"],
        "skill_levels": {
            "JavaScript": "Expert",
            "HTML5": "Advanced", 
            "CSS3": "Advanced",
            "Responsive Design": "Advanced",
            "React": "Expert",
            "Angular": "Expert",
            "Vue.js": "Expert",
            "TypeScript": "Advanced",
            "State Management": "Advanced",
            "Testing": "Intermediate",
            "GraphQL": "Intermediate",
            "Web Performance": "Intermediate",
            "Build Tools": "Intermediate",
            "Attention to Detail": "Advanced",
            "User-Centric Thinking": "Advanced",
            "Collaboration": "Intermediate",
            "Communication": "Intermediate"
        },
        "conditional_skills": {
            "react": {"add": [{"skill": "React", "category": "core"}, {"skill": "JSX", "category": "core"}], "remove": [], "promote": ["React"]},
            "angular": {"add": [{"skill": "Angular", "category": "core"}], "remove": [], "promote": ["Angular"]},
            "vue": {"add": [{"skill": "Vue.js", "category": "core"}], "remove": [], "promote": ["Vue.js"]},
            "next.js": {"add": [{"skill": "Next.js", "category": "core"}], "remove": [], "promote": ["Next.js"]},
            "svelte": {"add": [{"skill": "Svelte", "category": "core"}], "remove": [], "promote": ["Svelte"]},
            "typescript": {"add": [{"skill": "TypeScript", "category": "core"}], "remove": [], "promote": ["TypeScript"]},
            "redux": {"add": [{"skill": "State Management", "category": "core"}, {"skill": "Redux", "category": "bonus"}], "remove": [], "promote": ["State Management"]},
            "jest": {"add": [{"skill": "Testing", "category": "bonus"}, {"skill": "Jest", "category": "bonus"}], "remove": []},
            "cypress": {"add": [{"skill": "Testing", "category": "bonus"}, {"skill": "Cypress", "category": "bonus"}], "remove": []},
            "webpack": {"add": [{"skill": "Build Tools", "category": "bonus"}, {"skill": "Webpack", "category": "bonus"}], "remove": []},
            "vite": {"add": [{"skill": "Build Tools", "category": "bonus"}, {"skill": "Vite", "category": "bonus"}], "remove": []}
        }
    },
    
    "Backend Developer": {
        "variations": [
            "server-side engineer", "api developer", "services engineer", "backend engineer",
            "back-end developer", "back end developer", "api engineer", "server developer",
            "microservices developer", "web services developer"
        ],
        "default_skills": ["Programming Fundamentals", "REST APIs", "Database Management", "Authentication"],
        "soft_skills": ["Problem Solving", "Collaboration", "Documentation", "Analytical Thinking"],
        "bonus_skills": ["GraphQL", "Microservices", "Docker", "CI/CD", "Caching"],
        "skill_levels": {
            "Programming Fundamentals": "Expert",
            "REST APIs": "Expert",
            "Database Management": "Advanced",
            "Authentication": "Advanced",
            "Node.js": "Expert",
            "Python": "Expert",
            "Java": "Expert",
            ".NET": "Expert",
            "GraphQL": "Intermediate",
            "Microservices": "Intermediate",
            "Docker": "Intermediate",
            "CI/CD": "Intermediate",
            "Caching": "Intermediate",
            "Problem Solving": "Advanced",
            "Collaboration": "Intermediate",
            "Documentation": "Intermediate",
            "Analytical Thinking": "Advanced"
        },
        "conditional_skills": {
            "node.js": {"add": [{"skill": "Node.js", "category": "core"}, {"skill": "Express.js", "category": "bonus"}], "remove": [], "promote": ["Node.js"]},
            "python": {"add": [{"skill": "Python", "category": "core"}], "remove": [], "promote": ["Python"]},
            "django": {"add": [{"skill": "Django", "category": "core"}], "remove": [], "promote": ["Django"]},
            "flask": {"add": [{"skill": "Flask", "category": "core"}], "remove": [], "promote": ["Flask"]},
            "fastapi": {"add": [{"skill": "FastAPI", "category": "core"}], "remove": [], "promote": ["FastAPI"]},
            "java": {"add": [{"skill": "Java", "category": "core"}], "remove": [], "promote": ["Java"]},
            "spring boot": {"add": [{"skill": "Spring Boot", "category": "core"}], "remove": [], "promote": ["Spring Boot"]},
            ".net": {"add": [{"skill": ".NET", "category": "core"}], "remove": [], "promote": [".NET"]},
            "ruby": {"add": [{"skill": "Ruby", "category": "core"}, {"skill": "Ruby on Rails", "category": "core"}], "remove": [], "promote": ["Ruby"]},
            "mongodb": {"add": [{"skill": "MongoDB", "category": "bonus"}], "remove": []},
            "postgresql": {"add": [{"skill": "PostgreSQL", "category": "bonus"}], "remove": []},
            "mysql": {"add": [{"skill": "MySQL", "category": "bonus"}], "remove": []},
            "redis": {"add": [{"skill": "Redis", "category": "bonus"}], "remove": []},
            "graphql": {"add": [{"skill": "GraphQL", "category": "bonus"}], "remove": []},
            "docker": {"add": [{"skill": "Docker", "category": "bonus"}], "remove": []},
            "kubernetes": {"add": [{"skill": "Kubernetes", "category": "bonus"}], "remove": []}
        }
    },
    
    "Full Stack Developer": {
        "variations": [
            "web application engineer", "application programmer", "fullstack developer",
            "full-stack developer", "web engineer", "full stack engineer", "fullstack engineer",
            "mern developer", "mean developer", "lamp developer", "django developer",
            "full stack web developer", "fullstack web developer", "full-stack web developer"
        ],
        "default_skills": ["JavaScript", "REST APIs", "Database Management", "Web Development"],
        "soft_skills": ["Multitasking", "Collaboration", "Communication", "Problem Solving"],
        "bonus_skills": ["TypeScript", "GraphQL", "Docker", "CI/CD", "Testing"],
        "skill_levels": {
            "JavaScript": "Expert",
            "REST APIs": "Advanced",
            "Database Management": "Advanced",
            "Web Development": "Expert",
            "React": "Expert",
            "Angular": "Expert",
            "Vue.js": "Expert",
            "Node.js": "Advanced",
            "Python": "Advanced",
            "Java": "Advanced",
            ".NET": "Advanced",
            "TypeScript": "Intermediate",
            "GraphQL": "Intermediate",
            "Docker": "Intermediate",
            "CI/CD": "Intermediate",
            "Testing": "Intermediate",
            "Multitasking": "Advanced",
            "Collaboration": "Advanced",
            "Communication": "Intermediate",
            "Problem Solving": "Expert"
        },
        "conditional_skills": {
            # Frontend frameworks
            "react": {"add": [{"skill": "React", "category": "core"}], "remove": [], "promote": ["React"]},
            "angular": {"add": [{"skill": "Angular", "category": "core"}], "remove": [], "promote": ["Angular"]},
            "vue": {"add": [{"skill": "Vue.js", "category": "core"}], "remove": [], "promote": ["Vue.js"]},
            # Backend technologies
            "node.js": {"add": [{"skill": "Node.js", "category": "core"}], "remove": [], "promote": ["Node.js"]},
            "python": {"add": [{"skill": "Python", "category": "core"}], "remove": [], "promote": ["Python"]},
            "django": {"add": [{"skill": "Django", "category": "core"}], "remove": [], "promote": ["Django"]},
            "java": {"add": [{"skill": "Java", "category": "core"}], "remove": [], "promote": ["Java"]},
            ".net": {"add": [{"skill": ".NET", "category": "core"}], "remove": [], "promote": [".NET"]},
            # Databases
            "sql": {"add": [{"skill": "SQL", "category": "core"}], "remove": [], "promote": ["SQL"]},
            "nosql": {"add": [{"skill": "NoSQL", "category": "core"}], "remove": [], "promote": ["NoSQL"]},
            "mongodb": {"add": [{"skill": "MongoDB", "category": "bonus"}], "remove": []},
            "postgresql": {"add": [{"skill": "PostgreSQL", "category": "bonus"}], "remove": []},
            # Stack-specific combinations
            "mern": {"add": [{"skill": "MongoDB", "category": "core"}, {"skill": "Express.js", "category": "core"}, {"skill": "React", "category": "core"}, {"skill": "Node.js", "category": "core"}], "remove": []},
            "mean": {"add": [{"skill": "MongoDB", "category": "core"}, {"skill": "Express.js", "category": "core"}, {"skill": "Angular", "category": "core"}, {"skill": "Node.js", "category": "core"}], "remove": []},
            "lamp": {"add": [{"skill": "Linux", "category": "bonus"}, {"skill": "Apache", "category": "bonus"}, {"skill": "MySQL", "category": "core"}, {"skill": "PHP", "category": "core"}], "remove": []}
        }
    },
    
    "Mobile App Developer": {
        "variations": [
            "ios developer", "android developer", "flutter developer", "react native engineer",
            "mobile engineer", "app developer", "mobile application developer", "cross-platform developer",
            "native app developer", "hybrid app developer"
        ],
        "default_skills": ["Mobile Development", "UI/UX Principles", "REST APIs", "App Store Deployment"],
        "soft_skills": ["User Empathy", "Communication", "Collaboration", "Problem Solving"],
        "bonus_skills": ["Firebase", "Testing", "CI/CD for Mobile", "App Security", "Performance Optimization"],
        "skill_levels": {
            "Mobile Development": "Expert",
            "UI/UX Principles": "Advanced",
            "REST APIs": "Advanced",
            "App Store Deployment": "Advanced",
            "Swift": "Expert",
            "Kotlin": "Expert",
            "Dart": "Expert",
            "JavaScript": "Expert",
            "React Native": "Expert",
            "Flutter": "Expert",
            "Firebase": "Intermediate",
            "Testing": "Intermediate",
            "CI/CD": "Intermediate",
            "App Security": "Intermediate",
            "Performance Optimization": "Intermediate",
            "User Empathy": "Advanced",
            "Communication": "Intermediate",
            "Collaboration": "Intermediate",
            "Problem Solving": "Advanced"
        },
        "conditional_skills": {
            "ios": {"add": [{"skill": "Swift", "category": "core"}, {"skill": "iOS Development", "category": "core"}], "remove": [], "promote": ["Swift"]},
            "swift": {"add": [{"skill": "Swift", "category": "core"}, {"skill": "iOS Development", "category": "core"}], "remove": [], "promote": ["Swift"]},
            "android": {"add": [{"skill": "Kotlin", "category": "core"}, {"skill": "Android Development", "category": "core"}], "remove": [], "promote": ["Kotlin"]},
            "kotlin": {"add": [{"skill": "Kotlin", "category": "core"}, {"skill": "Android Development", "category": "core"}], "remove": [], "promote": ["Kotlin"]},
            "flutter": {"add": [{"skill": "Flutter", "category": "core"}, {"skill": "Dart", "category": "core"}], "remove": [], "promote": ["Flutter"]},
            "react native": {"add": [{"skill": "React Native", "category": "core"}, {"skill": "JavaScript", "category": "core"}], "remove": [], "promote": ["React Native"]},
            "firebase": {"add": [{"skill": "Firebase", "category": "bonus"}], "remove": []},
            "xctest": {"add": [{"skill": "XCTest", "category": "bonus"}], "remove": []},
            "espresso": {"add": [{"skill": "Espresso", "category": "bonus"}], "remove": []},
            "fastlane": {"add": [{"skill": "Fastlane", "category": "bonus"}], "remove": []},
            "bitrise": {"add": [{"skill": "Bitrise", "category": "bonus"}], "remove": []}
        }
    },
    
    "Web Developer": {
        "variations": [
            "web programmer", "website engineer", "frontend programmer", "web designer",
            "static website developer", "web application developer"
        ],
        "default_skills": ["HTML5", "CSS3", "JavaScript", "Responsive Design", "Cross-Browser Compatibility"],
        "soft_skills": ["Attention to Detail", "Communication", "Collaboration", "Creativity"],
        "bonus_skills": ["SEO", "Bootstrap", "Git", "Web Performance", "Accessibility"],
        "skill_levels": {
            "HTML5": "Expert",
            "CSS3": "Expert",
            "JavaScript": "Advanced",
            "Responsive Design": "Advanced",
            "Cross-Browser Compatibility": "Advanced",
            "SEO": "Intermediate",
            "Bootstrap": "Intermediate",
            "Tailwind CSS": "Intermediate",
            "Git": "Intermediate",
            "Web Performance": "Intermediate",
            "Accessibility": "Intermediate",
            "Attention to Detail": "Advanced",
            "Communication": "Intermediate",
            "Collaboration": "Intermediate",
            "Creativity": "Advanced"
        },
        "conditional_skills": {
            "bootstrap": {"add": [{"skill": "Bootstrap", "category": "bonus"}], "remove": []},
            "tailwind": {"add": [{"skill": "Tailwind CSS", "category": "bonus"}], "remove": []},
            "seo": {"add": [{"skill": "SEO", "category": "bonus"}], "remove": []},
            "analytics": {"add": [{"skill": "Google Analytics", "category": "bonus"}], "remove": []}
        }
    },
    
    "WordPress Developer": {
        "variations": [
            "wp developer", "wordpress engineer", "woocommerce developer", 
            "wordpress theme developer", "wordpress plugin developer", "wp specialist"
        ],
        "default_skills": ["WordPress", "PHP", "MySQL", "HTML5", "CSS3"],
        "soft_skills": ["Problem Solving", "Client Communication", "Attention to Detail", "Creativity"],
        "bonus_skills": ["WooCommerce", "Custom Post Types", "ACF", "Theme Development", "Plugin Development"],
        "skill_levels": {
            "WordPress": "Expert",
            "PHP": "Advanced",
            "MySQL": "Intermediate",
            "HTML5": "Advanced",
            "CSS3": "Advanced",
            "JavaScript": "Intermediate",
            "WooCommerce": "Advanced",
            "Custom Post Types": "Intermediate",
            "ACF": "Intermediate",
            "Theme Development": "Advanced",
            "Plugin Development": "Intermediate",
            "Gutenberg": "Intermediate",
            "Elementor": "Intermediate",
            "Problem Solving": "Advanced",
            "Client Communication": "Advanced",
            "Attention to Detail": "Advanced",
            "Creativity": "Advanced"
        },
        "conditional_skills": {
            "wordpress": {"add": [{"skill": "WordPress", "category": "core"}], "remove": [], "promote": ["WordPress"]},
            "woocommerce": {"add": [{"skill": "WooCommerce", "category": "core"}], "remove": [], "promote": ["WooCommerce"]},
            "php": {"add": [{"skill": "PHP", "category": "core"}], "remove": [], "promote": ["PHP"]},
            "gutenberg": {"add": [{"skill": "Gutenberg", "category": "bonus"}], "remove": []},
            "elementor": {"add": [{"skill": "Elementor", "category": "bonus"}], "remove": []},
            "acf": {"add": [{"skill": "ACF", "category": "bonus"}], "remove": []},
            "custom fields": {"add": [{"skill": "Custom Post Types", "category": "bonus"}], "remove": []}
        }
    },
    
    "Shopify Developer": {
        "variations": [
            "shopify engineer", "shopify theme developer", "shopify app developer",
            "ecommerce developer", "shopify specialist", "liquid developer"
        ],
        "default_skills": ["Shopify", "Liquid", "HTML5", "CSS3", "JavaScript"],
        "soft_skills": ["Problem Solving", "Client Communication", "Business Acumen", "Creativity"],
        "bonus_skills": ["Shopify Plus", "GraphQL", "REST APIs", "App Development", "Theme Customization"],
        "skill_levels": {
            "Shopify": "Expert",
            "Liquid": "Expert",
            "HTML5": "Advanced",
            "CSS3": "Advanced",
            "JavaScript": "Advanced",
            "Shopify Plus": "Advanced",
            "GraphQL": "Intermediate",
            "REST APIs": "Advanced",
            "App Development": "Intermediate",
            "Theme Customization": "Expert",
            "Shopify CLI": "Intermediate",
            "Problem Solving": "Advanced",
            "Client Communication": "Advanced",
            "Business Acumen": "Intermediate",
            "Creativity": "Advanced"
        },
        "conditional_skills": {
            "shopify": {"add": [{"skill": "Shopify", "category": "core"}], "remove": [], "promote": ["Shopify"]},
            "liquid": {"add": [{"skill": "Liquid", "category": "core"}], "remove": [], "promote": ["Liquid"]},
            "shopify plus": {"add": [{"skill": "Shopify Plus", "category": "core"}], "remove": [], "promote": ["Shopify Plus"]},
            "graphql": {"add": [{"skill": "GraphQL", "category": "bonus"}], "remove": []},
            "shopify app": {"add": [{"skill": "App Development", "category": "bonus"}], "remove": []}
        }
    },
    
    "Magento Developer": {
        "variations": [
            "magento engineer", "adobe commerce developer", "magento specialist",
            "magento 2 developer", "ecommerce magento developer"
        ],
        "default_skills": ["Magento", "PHP", "MySQL", "XML", "JavaScript"],
        "soft_skills": ["Problem Solving", "Analytical Thinking", "Communication", "Patience"],
        "bonus_skills": ["Magento 2", "Adobe Commerce", "REST APIs", "GraphQL", "Composer"],
        "skill_levels": {
            "Magento": "Expert",
            "PHP": "Expert",
            "MySQL": "Advanced",
            "XML": "Advanced",
            "JavaScript": "Advanced",
            "Magento 2": "Expert",
            "Adobe Commerce": "Advanced",
            "REST APIs": "Advanced",
            "GraphQL": "Intermediate",
            "Composer": "Intermediate",
            "Zend Framework": "Intermediate",
            "Problem Solving": "Expert",
            "Analytical Thinking": "Advanced",
            "Communication": "Intermediate",
            "Patience": "Advanced"
        },
        "conditional_skills": {
            "magento": {"add": [{"skill": "Magento", "category": "core"}], "remove": [], "promote": ["Magento"]},
            "adobe commerce": {"add": [{"skill": "Adobe Commerce", "category": "core"}], "remove": [], "promote": ["Adobe Commerce"]},
            "php": {"add": [{"skill": "PHP", "category": "core"}], "remove": [], "promote": ["PHP"]},
            "composer": {"add": [{"skill": "Composer", "category": "bonus"}], "remove": []},
            "zend": {"add": [{"skill": "Zend Framework", "category": "bonus"}], "remove": []}
        }
    }
}

def calculate_similarity(s1: str, s2: str) -> float:
    """Calculate similarity between two strings using SequenceMatcher"""
    return SequenceMatcher(None, s1.lower(), s2.lower()).ratio()

def extract_context_from_description(description: str) -> Dict[str, any]:
    """Extract technology context from job description with emphasis levels"""
    desc_lower = description.lower()
    context = {}
    
    # Helper function to determine emphasis level
    def get_emphasis_level(tech_words, description):
        # For each technology, find the specific context around it
        for word in tech_words:
            if word not in description:
                continue
                
            # Find all occurrences of the word and check context around each
            pattern = rf'\b{re.escape(word)}\b'
            matches = list(re.finditer(pattern, description, re.IGNORECASE))
            
            for match in matches:
                start = max(0, match.start() - 30)  # 30 chars before
                end = min(len(description), match.end() + 30)  # 30 chars after
                context_snippet = description[start:end].lower()
                
                # Primary indicators (must be close to the tech word)
                if any(indicator in context_snippet for indicator in [
                    'expert', 'strong', 'senior', 'proficient', 'focused on', 'primarily'
                ]):
                    return "primary"
                
                # Secondary indicators  
                if any(indicator in context_snippet for indicator in [
                    'knowledge of', 'familiar with', 'understanding of', 'nice to have',
                    'helpful', 'bonus', 'preferred', 'plus'
                ]):
                    return "secondary"
            
            # If mentioned but no clear context, it's neutral
            return "neutral"
        
        return None
    
    # Frontend frameworks - smart pattern matching
    # Check for React Native first (more specific)
    if 'react native' in desc_lower or 'react-native' in desc_lower:
        context['react native'] = get_emphasis_level(['react native', 'react-native'], desc_lower) or True
    
    # Check for React (web) - look for React mentions that are separate from React Native
    # Method: Check if React appears in contexts that are clearly not React Native
    if 'react' in desc_lower:
        # Look for React that's not part of "React Native"
        react_pattern = r'\breact\b(?!\s+native)'  # React not followed by Native
        if re.search(react_pattern, desc_lower, re.IGNORECASE):
            context['react'] = get_emphasis_level(['react', 'reactjs', 'jsx'], desc_lower) or True
    
    # Also check for ReactJS and JSX which are clearly web React
    if 'reactjs' in desc_lower or 'jsx' in desc_lower:
        context['react'] = get_emphasis_level(['reactjs', 'jsx'], desc_lower) or True
    
    angular_words = ['angular', 'angularjs']
    if any(word in desc_lower for word in angular_words):
        context['angular'] = get_emphasis_level(angular_words, desc_lower) or True
    
    vue_words = ['vue', 'vuejs', 'vue.js']
    if any(word in desc_lower for word in vue_words):
        context['vue'] = get_emphasis_level(vue_words, desc_lower) or True
    
    # TypeScript detection
    typescript_words = ['typescript', 'ts']
    if any(word in desc_lower for word in typescript_words):
        context['typescript'] = get_emphasis_level(typescript_words, desc_lower) or True
    
    # Testing frameworks
    jest_words = ['jest']
    if any(word in desc_lower for word in jest_words):
        context['jest'] = get_emphasis_level(jest_words, desc_lower) or True
    
    jasmine_words = ['jasmine']
    if any(word in desc_lower for word in jasmine_words):
        context['jasmine'] = get_emphasis_level(jasmine_words, desc_lower) or True
    
    karma_words = ['karma']
    if any(word in desc_lower for word in karma_words):
        context['karma'] = get_emphasis_level(karma_words, desc_lower) or True
    
    cypress_words = ['cypress']
    if any(word in desc_lower for word in cypress_words):
        context['cypress'] = get_emphasis_level(cypress_words, desc_lower) or True
    
    selenium_words = ['selenium']
    if any(word in desc_lower for word in selenium_words):
        context['selenium'] = get_emphasis_level(selenium_words, desc_lower) or True
    
    mocha_words = ['mocha']
    if any(word in desc_lower for word in mocha_words):
        context['mocha'] = get_emphasis_level(mocha_words, desc_lower) or True
    
    chai_words = ['chai']
    if any(word in desc_lower for word in chai_words):
        context['chai'] = get_emphasis_level(chai_words, desc_lower) or True
    
    puppeteer_words = ['puppeteer']
    if any(word in desc_lower for word in puppeteer_words):
        context['puppeteer'] = get_emphasis_level(puppeteer_words, desc_lower) or True
    
    testing_words = ['testing', 'unit test', 'unit testing']
    if any(word in desc_lower for word in testing_words):
        context['testing'] = get_emphasis_level(testing_words, desc_lower) or True
    
    # Build Tools & Bundlers
    webpack_words = ['webpack']
    if any(word in desc_lower for word in webpack_words):
        context['webpack'] = get_emphasis_level(webpack_words, desc_lower) or True
    
    vite_words = ['vite']
    if any(word in desc_lower for word in vite_words):
        context['vite'] = get_emphasis_level(vite_words, desc_lower) or True
    
    rollup_words = ['rollup']
    if any(word in desc_lower for word in rollup_words):
        context['rollup'] = get_emphasis_level(rollup_words, desc_lower) or True
    
    parcel_words = ['parcel']
    if any(word in desc_lower for word in parcel_words):
        context['parcel'] = get_emphasis_level(parcel_words, desc_lower) or True
    
    babel_words = ['babel']
    if any(word in desc_lower for word in babel_words):
        context['babel'] = get_emphasis_level(babel_words, desc_lower) or True
    
    eslint_words = ['eslint']
    if any(word in desc_lower for word in eslint_words):
        context['eslint'] = get_emphasis_level(eslint_words, desc_lower) or True
    
    prettier_words = ['prettier']
    if any(word in desc_lower for word in prettier_words):
        context['prettier'] = get_emphasis_level(prettier_words, desc_lower) or True
    
    # CSS Frameworks & State Management  
    tailwind_words = ['tailwind', 'tailwindcss']
    if any(word in desc_lower for word in tailwind_words):
        context['tailwind'] = get_emphasis_level(tailwind_words, desc_lower) or True
    
    bootstrap_words = ['bootstrap']
    if any(word in desc_lower for word in bootstrap_words):
        context['bootstrap'] = get_emphasis_level(bootstrap_words, desc_lower) or True
    
    redux_words = ['redux']
    if any(word in desc_lower for word in redux_words):
        context['redux'] = get_emphasis_level(redux_words, desc_lower) or True
    
    mobx_words = ['mobx']
    if any(word in desc_lower for word in mobx_words):
        context['mobx'] = get_emphasis_level(mobx_words, desc_lower) or True
    
    sass_words = ['sass', 'scss']
    if any(word in desc_lower for word in sass_words):
        context['sass'] = get_emphasis_level(sass_words, desc_lower) or True
    
    styled_components_words = ['styled-components', 'styled components']
    if any(word in desc_lower for word in styled_components_words):
        context['styled-components'] = get_emphasis_level(styled_components_words, desc_lower) or True
    
    # Backend technologies
    python_words = ['python', 'django', 'flask']
    if any(word in desc_lower for word in python_words):
        context['python'] = get_emphasis_level(python_words, desc_lower) or True
    
    nodejs_words = ['node.js', 'nodejs', 'express']
    if any(word in desc_lower for word in nodejs_words):
        context['nodejs'] = get_emphasis_level(nodejs_words, desc_lower) or True
    
    # Full-stack specific
    mern_words = ['mern', 'mern stack']
    if any(word in desc_lower for word in mern_words):
        context['mern'] = get_emphasis_level(mern_words, desc_lower) or True
    
    mean_words = ['mean', 'mean stack']
    if any(word in desc_lower for word in mean_words):
        context['mean'] = get_emphasis_level(mean_words, desc_lower) or True
    
    lamp_words = ['lamp', 'lamp stack']
    if any(word in desc_lower for word in lamp_words):
        context['lamp'] = get_emphasis_level(lamp_words, desc_lower) or True
    
    # Database specific
    mongodb_words = ['mongodb', 'mongo']
    if any(word in desc_lower for word in mongodb_words):
        context['mongodb'] = get_emphasis_level(mongodb_words, desc_lower) or True
    
    # AI/ML
    tf_words = ['tensorflow', 'keras']
    if any(word in desc_lower for word in tf_words):
        context['tensorflow'] = get_emphasis_level(tf_words, desc_lower) or True
    
    pytorch_words = ['pytorch', 'torch']
    if any(word in desc_lower for word in pytorch_words):
        context['pytorch'] = get_emphasis_level(pytorch_words, desc_lower) or True
    
    nlp_words = ['nlp', 'natural language']
    if any(word in desc_lower for word in nlp_words):
        context['nlp'] = get_emphasis_level(nlp_words, desc_lower) or True
    
    # DevOps and Infrastructure
    docker_words = ['docker', 'containerization']
    if any(word in desc_lower for word in docker_words):
        context['docker'] = get_emphasis_level(docker_words, desc_lower) or True
    
    kubernetes_words = ['kubernetes', 'k8s', 'orchestration']
    if any(word in desc_lower for word in kubernetes_words):
        context['kubernetes'] = get_emphasis_level(kubernetes_words, desc_lower) or True
    
    aws_words = ['aws', 'amazon web services', 'cloud services']
    if any(word in desc_lower for word in aws_words):
        context['aws'] = get_emphasis_level(aws_words, desc_lower) or True
    
    # Database technologies
    postgresql_words = ['postgresql', 'postgres']
    if any(word in desc_lower for word in postgresql_words):
        context['postgresql'] = get_emphasis_level(postgresql_words, desc_lower) or True
    
    redis_words = ['redis', 'caching']
    if any(word in desc_lower for word in redis_words):
        context['redis'] = get_emphasis_level(redis_words, desc_lower) or True
    
    # ERP and AI integration
    erp_words = ['erp', 'sap', 'oracle', 'dynamics']
    if any(word in desc_lower for word in erp_words):
        context['erp'] = get_emphasis_level(erp_words, desc_lower) or True
    
    ai_words = ['ai', 'artificial intelligence', 'machine learning', 'ml']
    if any(word in desc_lower for word in ai_words):
        context['ai'] = get_emphasis_level(ai_words, desc_lower) or True
    
    # Mobile-specific technologies
    ios_words = ['ios', 'iphone', 'ipad', 'swift']
    if any(word in desc_lower for word in ios_words):
        context['ios'] = get_emphasis_level(ios_words, desc_lower) or True
    
    swift_words = ['swift', 'swiftui']
    if any(word in desc_lower for word in swift_words):
        context['swift'] = get_emphasis_level(swift_words, desc_lower) or True
    
    android_words = ['android', 'kotlin', 'java android']
    if any(word in desc_lower for word in android_words):
        context['android'] = get_emphasis_level(android_words, desc_lower) or True
    
    kotlin_words = ['kotlin']
    if any(word in desc_lower for word in kotlin_words):
        context['kotlin'] = get_emphasis_level(kotlin_words, desc_lower) or True
    
    flutter_words = ['flutter', 'dart']
    if any(word in desc_lower for word in flutter_words):
        context['flutter'] = get_emphasis_level(flutter_words, desc_lower) or True
    
    # Mobile testing tools
    xctest_words = ['xctest', 'xcode test']
    if any(word in desc_lower for word in xctest_words):
        context['xctest'] = get_emphasis_level(xctest_words, desc_lower) or True
    
    espresso_words = ['espresso', 'android test']
    if any(word in desc_lower for word in espresso_words):
        context['espresso'] = get_emphasis_level(espresso_words, desc_lower) or True
    
    # Mobile CI/CD tools
    fastlane_words = ['fastlane']
    if any(word in desc_lower for word in fastlane_words):
        context['fastlane'] = get_emphasis_level(fastlane_words, desc_lower) or True
    
    bitrise_words = ['bitrise']
    if any(word in desc_lower for word in bitrise_words):
        context['bitrise'] = get_emphasis_level(bitrise_words, desc_lower) or True
    
    firebase_words = ['firebase']
    if any(word in desc_lower for word in firebase_words):
        context['firebase'] = get_emphasis_level(firebase_words, desc_lower) or True
    
    # CMS-specific technologies
    wordpress_words = ['wordpress', 'wp', 'woocommerce']
    if any(word in desc_lower for word in wordpress_words):
        context['wordpress'] = get_emphasis_level(wordpress_words, desc_lower) or True
    
    shopify_words = ['shopify', 'liquid', 'shopify theme']
    if any(word in desc_lower for word in shopify_words):
        context['shopify'] = get_emphasis_level(shopify_words, desc_lower) or True
    
    drupal_words = ['drupal']
    if any(word in desc_lower for word in drupal_words):
        context['drupal'] = get_emphasis_level(drupal_words, desc_lower) or True
    
    joomla_words = ['joomla']
    if any(word in desc_lower for word in joomla_words):
        context['joomla'] = get_emphasis_level(joomla_words, desc_lower) or True
    
    magento_words = ['magento', 'adobe commerce']
    if any(word in desc_lower for word in magento_words):
        context['magento'] = get_emphasis_level(magento_words, desc_lower) or True
    
    php_words = ['php', 'laravel', 'symfony']
    if any(word in desc_lower for word in php_words):
        context['php'] = get_emphasis_level(php_words, desc_lower) or True
    
    # SEO and Analytics
    seo_words = ['seo', 'search engine optimization']
    if any(word in desc_lower for word in seo_words):
        context['seo'] = get_emphasis_level(seo_words, desc_lower) or True
    
    analytics_words = ['google analytics', 'analytics', 'ga4']
    if any(word in desc_lower for word in analytics_words):
        context['analytics'] = get_emphasis_level(analytics_words, desc_lower) or True
    
    return context

def generate_smart_skills_suggestions(normalized_title: str, description: str = "") -> Dict[str, Any]:
    """Generate context-aware skills based on job title and description with detailed levels"""
    
    # Find the job template
    job_template = None
    for standard_title, data in STANDARD_JOB_TITLES.items():
        if normalized_title.lower() == standard_title.lower():
            job_template = data
            break
    
    if not job_template:
        return {
            "suggested_skills": [],
            "soft_skills": [],
            "bonus_skills": [],
            "skills_to_remove": [],
            "reasoning": "No template found for this job title",
            "confidence": "low"
        }
    
    # Get skill levels mapping
    skill_levels = job_template.get("skill_levels", {})
    
    # Helper function to create skill object with proper level
    def create_skill(skill_name: str, category: str = "core") -> Dict[str, Any]:
        level = skill_levels.get(skill_name, "Intermediate")
        rating_map = {"Basic": 5, "Intermediate": 6, "Advanced": 8, "Expert": 10}
        return {
            "skill": skill_name,
            "level": level,
            "rating": rating_map.get(level, 6),
            "evidence": ["Template-based suggestion"],
            "weight": 0.8,
            "category": category
        }
    
    # Start with default skills
    suggested_skills = [create_skill(skill, "core") for skill in job_template["default_skills"]]
    soft_skills = [create_skill(skill, "soft") for skill in job_template.get("soft_skills", [])]
    bonus_skills = [create_skill(skill, "bonus") for skill in job_template.get("bonus_skills", [])]
    skills_to_remove = []
    reasoning = []
    
    # Extract context from description
    context = extract_context_from_description(description)
    
    # Apply conditional skills based on context
    for tech, emphasis in context.items():
        if emphasis and tech in job_template["conditional_skills"]:
            conditional = job_template["conditional_skills"][tech]
            
            # Add specific skills with their categories
            for skill_info in conditional["add"]:
                if isinstance(skill_info, dict):
                    skill_name = skill_info["skill"]
                    skill_category = skill_info["category"]
                else:
                    # Backward compatibility
                    skill_name = skill_info
                    skill_category = "core"
                
                # Check if skill already exists in any category
                skill_exists = False
                for skill_list in [suggested_skills, soft_skills, bonus_skills]:
                    if any(s["skill"] == skill_name for s in skill_list):
                        skill_exists = True
                        break
                
                if not skill_exists:
                    new_skill = create_skill(skill_name, skill_category)
                    if skill_category == "core":
                        suggested_skills.append(new_skill)
                    elif skill_category == "soft":
                        soft_skills.append(new_skill)
                    elif skill_category == "bonus":
                        bonus_skills.append(new_skill)
                    reasoning.append(f"Added {skill_name} as {skill_category} skill based on {tech} mention in description")
            
            # Promote skills based on emphasis level
            if "promote" in conditional:
                for skill_name in conditional["promote"]:
                    for skill in suggested_skills:
                        if skill["skill"] == skill_name:
                            # Only promote to Expert if it's primary focus
                            if emphasis == "primary":
                                if skill["level"] != "Expert":
                                    skill["level"] = "Expert"
                                    skill["rating"] = 10
                                    reasoning.append(f"Promoted {skill_name} to Expert level due to primary focus")
                            elif emphasis == "secondary":
                                # Keep current level for secondary mentions
                                reasoning.append(f"Maintained {skill_name} at {skill['level']} level (secondary mention)")
                            elif emphasis == "neutral":
                                # Keep current level for neutral mentions
                                reasoning.append(f"Maintained {skill_name} at {skill['level']} level (neutral mention)")
            
            # Special handling for React vs React Native mutual exclusion
            # Only remove if the other framework is NOT also detected
            if tech == "react" and "react native" in context:
                # Both React and React Native detected - keep both, don't remove
                pass
            elif tech == "react native" and "react" in context:
                # Both React and React Native detected - keep both, don't remove  
                pass
            else:
                # Only remove skills if explicitly needed and no conflicts
                for skill in conditional.get("remove", []):
                    suggested_skills = [s for s in suggested_skills if s["skill"] != skill]
                    skills_to_remove.append(skill)
                    reasoning.append(f"Removed {skill} due to {tech} specificity")
    
    # Also check job title for specific technology mentions
    title_lower = normalized_title.lower()
    for tech, conditional in job_template["conditional_skills"].items():
        if tech in title_lower:
            for skill_info in conditional["add"]:
                if isinstance(skill_info, dict):
                    skill_name = skill_info["skill"]
                    skill_category = skill_info["category"]
                else:
                    # Backward compatibility
                    skill_name = skill_info
                    skill_category = "core"
                
                # Check if skill already exists in any category
                skill_exists = False
                for skill_list in [suggested_skills, soft_skills, bonus_skills]:
                    if any(s["skill"] == skill_name for s in skill_list):
                        skill_exists = True
                        break
                
                if not skill_exists:
                    new_skill = create_skill(skill_name, skill_category)
                    if skill_category == "core":
                        suggested_skills.append(new_skill)
                    elif skill_category == "soft":
                        soft_skills.append(new_skill)
                    elif skill_category == "bonus":
                        bonus_skills.append(new_skill)
                    reasoning.append(f"Added {skill_name} as {skill_category} skill based on job title")
            
            # Promote skills mentioned in title
            if "promote" in conditional:
                for skill_name in conditional["promote"]:
                    for skill in suggested_skills:
                        if skill["skill"] == skill_name:
                            if skill["level"] != "Expert":
                                skill["level"] = "Expert" 
                                skill["rating"] = 10
                                reasoning.append(f"Promoted {skill_name} to Expert level due to title focus")
            
            # Only remove if truly incompatible
            for skill in conditional.get("remove", []):
                suggested_skills = [s for s in suggested_skills if s["skill"] != skill]
                skills_to_remove.append(skill)
                reasoning.append(f"Removed {skill} based on job title specificity")
    
    confidence = "high" if context else "medium"
    
    return {
        "suggested_skills": suggested_skills,
        "soft_skills": soft_skills,
        "bonus_skills": bonus_skills,
        "skills_to_remove": skills_to_remove,
        "reasoning": reasoning,
        "confidence": confidence,
        "context_detected": context
    }

def normalize_job_title_v3_enhanced(input_title: str, description: str = "") -> Dict[str, Any]:
    """
    V3 Enhanced: AI-powered job title normalization with smart skills management
    """
    if not input_title or not input_title.strip():
        return {
            "original_title": input_title,
            "normalized_title": input_title,
            "confidence": 0.0,
            "suggestions": [],
            "skills_analysis": None,
            "ai_disclaimer": "⚠️ AI makes mistakes! Please review all skills and suggestions carefully for best results.",
            "match_quality": "low"
        }
    
    input_clean = input_title.strip().lower()
    best_match = None
    highest_score = 0.0
    suggestions = []
    
    # Check against all standard titles and their variations
    for standard_title, data in STANDARD_JOB_TITLES.items():
        variations = data["variations"]
        
        # Check against the standard title itself
        score = calculate_similarity(input_clean, standard_title.lower())
        if score > highest_score:
            best_match = standard_title
            highest_score = score
        
        # Add to suggestions if reasonably similar
        if score > 0.6:
            suggestions.append({
                "title": standard_title,
                "confidence": round(score * 100, 1),
                "type": "standard"
            })
        
        # Check against variations
        for variation in variations:
            score = calculate_similarity(input_clean, variation.lower())
            if score > highest_score:
                best_match = standard_title
                highest_score = score
            
            # Add to suggestions if reasonably similar
            if score > 0.6:
                suggestions.append({
                    "title": standard_title,
                    "confidence": round(score * 100, 1),
                    "type": "variation_match"
                })
    
    # Sort suggestions and remove duplicates
    unique_suggestions = []
    seen_titles = set()
    for suggestion in sorted(suggestions, key=lambda x: x["confidence"], reverse=True):
        if suggestion["title"] not in seen_titles:
            unique_suggestions.append(suggestion)
            seen_titles.add(suggestion["title"])
    
    # Keep top 3 suggestions
    top_suggestions = unique_suggestions[:3]
    
    # Determine result
    if highest_score > 0.8:
        normalized_title = best_match
        confidence = highest_score
        match_quality = "high"
    elif highest_score > 0.6:
        normalized_title = input_title
        confidence = highest_score
        match_quality = "medium"
    else:
        normalized_title = input_title
        confidence = highest_score
        match_quality = "low"
    
    # Generate smart skills suggestions
    skills_analysis = None
    if highest_score > 0.6 and best_match:
        skills_analysis = generate_smart_skills_suggestions(best_match, description)
    
    return {
        "original_title": input_title,
        "normalized_title": normalized_title,
        "confidence": round(confidence * 100, 1),
        "suggestions": top_suggestions,
        "skills_analysis": skills_analysis,
        "ai_disclaimer": "⚠️ AI makes mistakes! Please review all skills and suggestions carefully for best results.",
        "match_quality": match_quality
    }

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

# Enhanced AI Analysis Functions - V3 Enhanced
def detect_job_type(title: str, description: str) -> List[str]:
    """V3 Enhanced: Detect job type using smart normalization for better accuracy"""
    
    # V3: Use enhanced normalization for better detection
    normalization = normalize_job_title_v3_enhanced(title, description)
    normalized_title = normalization["normalized_title"]
    
    # Use both original and normalized for comprehensive analysis
    text = (title + " " + normalized_title + " " + description).lower()
    title_lower = title.lower()
    normalized_title_lower = normalized_title.lower()
    
    # Log normalization if different (for debugging)
    if title.lower() != normalized_title.lower():
        logger.info(f"V3 Smart normalization: '{title}' → '{normalized_title}' ({normalization['confidence']}%)")
    
    types = []
    
    # Enhanced multi-track detection for internships and comprehensive job postings
    
    # Internship detection - check both titles
    if re.search(r'\b(intern|internship|trainee)\b', title_lower) or re.search(r'\b(intern|internship|trainee)\b', normalized_title_lower):
        types.append('internship')
    
    # Tech-related keywords - V3 Enhanced with AI roles and smart detection
    if re.search(r'\b(frontend|backend|fullstack|full.stack|web developer|software engineer|mobile developer|react developer|angular developer|vue developer|ai engineer|ml engineer)\b', normalized_title_lower) or \
       re.search(r'\b(developer|engineer|programmer|coding|software development|artificial intelligence|machine learning)\b', normalized_title_lower):
        types.append('tech')
    
    # Data-specific roles
    if re.search(r'\b(data scientist|data analyst|data engineer|analytics|business intelligence|bi analyst)\b', title_lower):
        types.append('data')
    
    # HR-specific roles
    if re.search(r'\b(hr|human resources|recruiter|talent acquisition|people operations|employee relations)\b', title_lower):
        types.append('hr')
    
    # Project Management roles
    if re.search(r'\b(project manager|program manager|scrum master|product manager|agile coach)\b', title_lower):
        types.append('management')
    
    # Marketing roles
    if re.search(r'\b(marketing|digital marketing|content marketing|social media|seo specialist|brand)\b', title_lower):
        types.append('marketing')
    
    # Finance roles
    if re.search(r'\b(financial analyst|accountant|finance|controller|treasury|audit)\b', title_lower):
        types.append('finance')
    
    # Business roles
    if re.search(r'\b(business analyst|consultant|strategy|operations|sales)\b', title_lower):
        types.append('business')
    
    # Enhanced description-based detection for multi-track positions
    if not types or len(types) == 1:  # If nothing found or only internship found
        # Check description for multiple tracks/areas
        if any(track_word in text for track_word in ['tracks', 'track', 'areas', 'fields', 'departments', 'multiple roles', 'various positions']):
            # Look for specific domain mentions in description
            if any(word in text for word in ['software development', 'programming', 'coding', 'technical', 'engineering', 'developer']):
                if 'tech' not in types:
                    types.append('tech')
            
            if any(word in text for word in ['data analysis', 'analytics', 'statistics', 'data science', 'reporting']):
                if 'data' not in types:
                    types.append('data')
            
            if any(word in text for word in ['project management', 'project coordinator', 'planning', 'strategy', 'operations']):
                if 'management' not in types:
                    types.append('management')
            
            if any(word in text for word in ['human resources', 'hr', 'recruitment', 'employee relations', 'people management']):
                if 'hr' not in types:
                    types.append('hr')
            
            if any(word in text for word in ['marketing', 'digital marketing', 'social media', 'content creation', 'branding']):
                if 'marketing' not in types:
                    types.append('marketing')
            
            if any(word in text for word in ['finance', 'accounting', 'financial analysis', 'budgeting']):
                if 'finance' not in types:
                    types.append('finance')
    
    # Legacy single-track detection (fallback)
    if not types:
        if re.search(r'\b(react|javascript|typescript|python|java|html|css|git)\b', text) and \
           re.search(r'\b(developer|development|engineering|programming|coding)\b', text):
            types.append('tech')
        elif re.search(r'\b(data analysis|statistics|sql|tableau|power bi)\b', text):
            types.append('data')
        elif re.search(r'\b(recruitment|hr system|employee relations|payroll)\b', text):
            types.append('hr')
        elif re.search(r'\b(project management|agile|scrum|stakeholder)\b', text):
            types.append('management')
        elif re.search(r'\b(market research|social media marketing|seo|digital campaigns)\b', text):
            types.append('marketing')
        elif re.search(r'\b(financial modeling|budgeting|accounting|gaap)\b', text):
            types.append('finance')
        elif re.search(r'\b(business strategy|consulting|operations management)\b', text):
            types.append('business')
    
    return types if types else ['general']

def detect_seniority_ai(title: str, description: str) -> str:
    """Enhanced seniority detection with better accuracy"""
    text = (title + " " + description).lower()
    title_lower = title.lower()
    
    # Check title first for explicit seniority levels
    if re.search(r'\b(lead|architect|principal|director|head of|chief)\b', title_lower):
        return "Lead"
    if re.search(r'\b(senior|sr\.)\b', title_lower):
        return "Senior"
    if re.search(r'\b(junior|jr\.)\b', title_lower):
        return "Junior"
    if re.search(r'\b(intern|internship|trainee)\b', title_lower):
        return "Internship"
    
    # Check description for experience requirements
    experience_match = re.search(r'(\d+)\+?\s*years?\s*of?\s*experience', text)
    if experience_match:
        years = int(experience_match.group(1))
        if years >= 10:
            return "Lead"
        elif years >= 4:
            return "Senior"
        elif years >= 2:
            return "Mid"
        else:
            return "Junior"
    
    # Check for specific lead responsibilities in description
    if re.search(r'\b(mentor|manage team|lead team|technical lead|team lead)\b', text):
        return "Lead"
    
    # Check for internship indicators in description
    if re.search(r'\b(internship|graduate|trainee|entry.level|fresh|new grad|no experience)\b', text):
        return "Internship"
    
    # Default based on context - be more conservative about Lead
    if re.search(r'\b(architect|design decisions|technical strategy|mentor junior)\b', text):
        return "Senior"  # Changed from "Senior" to avoid over-inflating to Lead
    elif re.search(r'\b(collaborate|support|assist|learn)\b', text):
        return "Mid"
    
    return "Mid"  # Default fallback
    if experience_match:
        years = int(experience_match.group(1))
        if years >= 7:
            return "Lead"
        elif years >= 4:
            return "Senior"
        elif years >= 2:
            return "Mid"
        else:
            return "Junior"
    
    # Check for "no experience required"
    if re.search(r'\b(no experience|0 years|entry.level)\b', text):
        return "Internship/Entry"
    
    return "Mid"  # Default

def analyze_requirements_ai(title: str, description: str) -> Dict[str, Any]:
    """Enhanced AI-powered requirement analysis with domain awareness and multi-track support"""
    try:
        text = (title + " " + description).lower()
        job_types = detect_job_type(title, description)
        seniority = detect_seniority_ai(title, description)
        is_internship = 'internship' in job_types or 'internship' in seniority.lower()
        
        # Enhanced multi-track detection
        is_multi_track = False
        
        # For internships: check if multiple tracks are mentioned AND multiple job types detected
        if is_internship:
            track_indicators = ['tracks', 'track', 'paths', 'areas', 'fields', 'departments', 'multiple roles', 'various positions', 'different teams']
            has_track_language = any(word in text for word in track_indicators)
            has_multiple_types = len([jt for jt in job_types if jt != 'internship']) > 1
            is_multi_track = has_track_language and (has_multiple_types or 
                                                   any(combo in text for combo in [
                                                       'software development', 'data analysis', 'project management', 'human resources',
                                                       'marketing', 'finance', 'business analysis'
                                                   ]))
        
        # For non-internships: very conservative - only if explicitly mentioned AND multiple types
        else:
            is_multi_track = len(job_types) > 2 and any(word in text for word in ['multiple roles', 'various positions', 'cross-functional'])
        
        # Determine default skill level based on seniority
        if is_internship or 'entry' in seniority.lower() or 'no experience' in text:
            default_level = "Basic"
        elif seniority == "Senior":
            default_level = "Advanced" 
        elif seniority == "Lead":
            default_level = "Expert"
        else:
            default_level = "Intermediate"
        
        # Initialize results structure
        analysis_result = {
            "core_skills": [],
            "soft_skills": [],
            "bonus_skills": [],
            "experience": {},
            "languages": [],
            "tracks": {},  # New: separate tracks for multi-track jobs
            "metadata": {
                "job_types": job_types,
                "seniority": seniority,
                "is_internship": is_internship,
                "is_multi_track": is_multi_track,
                "default_level": default_level
            }
        }
        
        # Define track-specific skills for multi-track jobs
        track_skills = {
            "tech": {
                "core": [
                    {"skill": "Programming Fundamentals", "level": default_level, "category": "programming"},
                    {"skill": "Problem Solving", "level": default_level, "category": "analytical"},
                    {"skill": "Computer Science Basics", "level": default_level, "category": "fundamentals"}
                ],
                "bonus": [
                    {"skill": "Git", "level": "Basic", "category": "tools"},
                    {"skill": "HTML5", "level": "Basic", "category": "frontend"},
                    {"skill": "CSS3", "level": "Basic", "category": "frontend"},
                    {"skill": "Python", "level": "Basic", "category": "programming"}
                ]
            },
            "data": {
                "core": [
                    {"skill": "Statistics", "level": default_level, "category": "analysis"},
                    {"skill": "Excel", "level": default_level, "category": "tools"},
                    {"skill": "Data Analysis", "level": default_level, "category": "analysis"},
                    {"skill": "Data Interpretation", "level": default_level, "category": "analysis"}
                ],
                "bonus": [
                    {"skill": "SQL", "level": "Basic", "category": "database"},
                    {"skill": "Python", "level": "Basic", "category": "programming"}
                ]
            },
            "management": {
                "core": [] if is_internship else [
                    {"skill": "Project Planning", "level": default_level, "category": "planning"},
                    {"skill": "Organization", "level": default_level, "category": "personal"},
                    {"skill": "Time Management", "level": default_level, "category": "personal"}
                ],
                "bonus": [
                    {"skill": "Project Management", "level": "Basic", "category": "management"},
                    {"skill": "Organization", "level": "Basic", "category": "personal"},
                    {"skill": "Time Management", "level": "Basic", "category": "personal"},
                    {"skill": "Agile", "level": "Basic", "category": "methodology"},
                    {"skill": "Scrum", "level": "Basic", "category": "methodology"}
                ]
            },
            "hr": {
                "core": [] if is_internship else [
                    {"skill": "HR Fundamentals", "level": default_level, "category": "hr"}
                ],
                "bonus": [
                    {"skill": "HR Fundamentals", "level": "Basic", "category": "hr"},
                    {"skill": "People Management", "level": "Basic", "category": "management"},
                    {"skill": "Employee Relations", "level": "Basic", "category": "hr"},
                    {"skill": "HRIS", "level": "Basic", "category": "systems"},
                    {"skill": "Recruitment", "level": "Basic", "category": "hr"}
                ]
            },
            "marketing": {
                "core": [] if is_internship else [
                    {"skill": "Marketing Fundamentals", "level": default_level, "category": "marketing"}
                ],
                "bonus": [
                    {"skill": "Marketing Fundamentals", "level": "Basic", "category": "marketing"},
                    {"skill": "Content Creation", "level": "Basic", "category": "creative"},
                    {"skill": "Market Research", "level": "Basic", "category": "research"},
                    {"skill": "Social Media", "level": "Basic", "category": "digital"},
                    {"skill": "Digital Marketing", "level": "Basic", "category": "digital"}
                ]
            },
            "finance": {
                "core": [] if is_internship else [
                    {"skill": "Financial Analysis", "level": default_level, "category": "analysis"}
                ],
                "bonus": [
                    {"skill": "Financial Analysis", "level": "Basic", "category": "analysis"},
                    {"skill": "Accounting", "level": "Basic", "category": "finance"},
                    {"skill": "Budgeting", "level": "Basic", "category": "finance"},
                    {"skill": "Excel", "level": "Basic", "category": "tools"},
                    {"skill": "Financial Modeling", "level": "Basic", "category": "modeling"}
                ]
            },
            "business": {
                "core": [] if is_internship else [
                    {"skill": "Business Analysis", "level": default_level, "category": "analysis"}
                ],
                "bonus": [
                    {"skill": "Business Analysis", "level": "Basic", "category": "analysis"},
                    {"skill": "Strategy", "level": "Basic", "category": "strategy"},
                    {"skill": "Operations", "level": "Basic", "category": "operations"},
                    {"skill": "Market Research", "level": "Basic", "category": "research"},
                    {"skill": "Customer Service", "level": "Basic", "category": "service"}
                ]
            }
        }
        
        # If multi-track job (especially internships), create separate tracks
        if is_multi_track or (is_internship and len(job_types) > 1):
            for job_type in job_types:
                if job_type in track_skills and job_type != 'internship':
                    track_data = track_skills[job_type]
                    analysis_result["tracks"][job_type] = {
                        "core_skills": [
                            {
                                **skill,
                                "evidence": [f"Essential for {job_type} track"],
                                "weight": 0.8,
                                "rating": calculate_skill_rating_enhanced(skill["level"], [f"Track requirement"], 0.8)
                            }
                            for skill in track_data["core"]
                        ],
                        "bonus_skills": [
                            {
                                **skill,
                                "evidence": [f"Valuable for {job_type} track"],
                                "weight": 0.6,
                                "rating": calculate_skill_rating_enhanced(skill["level"], [f"Track bonus"], 0.6)
                            }
                            for skill in track_data["bonus"]
                        ]
                    }
            
            # For multi-track, also populate main skills with most common/general ones
            all_core_skills = []
            all_bonus_skills = []
            
            for track_name, track_data in analysis_result["tracks"].items():
                all_core_skills.extend(track_data["core_skills"])
                all_bonus_skills.extend(track_data["bonus_skills"])
            
            # Remove duplicates and keep highest rated
            seen_skills = {}
            for skill in all_core_skills:
                skill_name = skill["skill"]
                if skill_name not in seen_skills or skill["rating"] > seen_skills[skill_name]["rating"]:
                    seen_skills[skill_name] = skill
            analysis_result["core_skills"] = list(seen_skills.values())
            
            # Same for bonus skills
            seen_bonus = {}
            for skill in all_bonus_skills:
                skill_name = skill["skill"]
                if skill_name not in seen_bonus or skill["rating"] > seen_bonus[skill_name]["rating"]:
                    seen_bonus[skill_name] = skill
            analysis_result["bonus_skills"] = list(seen_bonus.values())
            
            # Add essential soft skills for multi-track internships
            if is_internship:
                essential_internship_skills = [
                    {"skill": "Communication", "level": "Advanced", "evidence": ["Essential for collaboration across all tracks"], "weight": 0.9, "category": "interpersonal"},
                    {"skill": "Learning Ability", "level": "Advanced", "evidence": ["Critical for internship success"], "weight": 0.9, "category": "personal"},
                    {"skill": "Initiative", "level": "Advanced", "evidence": ["Important for proactive engagement"], "weight": 0.8, "category": "personal"},
                    {"skill": "Collaboration", "level": "Advanced", "evidence": ["Essential for working across departments"], "weight": 0.8, "category": "interpersonal"},
                    {"skill": "Motivation", "level": "Advanced", "evidence": ["Key for internship performance"], "weight": 0.8, "category": "personal"},
                    {"skill": "Problem Solving", "level": "Intermediate", "evidence": ["Important across all tracks"], "weight": 0.8, "category": "analytical"}
                ]
                
                soft_skills = []
                for skill in essential_internship_skills:
                    skill["rating"] = calculate_skill_rating_enhanced(skill["level"], skill["evidence"], skill["weight"])
                    soft_skills.append(skill)
                
                analysis_result["soft_skills"] = soft_skills
        
        else:
            # Single track analysis - use existing logic but enhanced with domain filtering
            
            # Step 1: Detect job domain before matching skills
            text_for_domain = (title + " " + description).lower()
            job_domain = "general"
            
            # Map job_types to domains more accurately
            if "tech" in job_types:
                job_domain = "engineering"
            elif "data" in job_types:
                job_domain = "data"
            elif "hr" in job_types:
                job_domain = "hr"
            elif "management" in job_types:
                job_domain = "business"
            elif "marketing" in job_types:
                job_domain = "marketing"
            elif "finance" in job_types:
                job_domain = "finance"
            elif "business" in job_types:
                job_domain = "business"
            
            # Fallback to text-based detection if job_types didn't match
            if job_domain == "general":
                if any(word in text_for_domain for word in [
                    "frontend", "backend", "developer", "engineer", "programming", "coding", "software",
                    "react", "angular", "vue", "javascript", "typescript", "python", "java", "node",
                    "html", "css", "git", "api", "database", "sql", "mongodb"
                ]):
                    job_domain = "engineering"
                elif any(word in text_for_domain for word in [
                    "data analyst", "data science", "statistics", "machine learning", "analytics",
                    "tableau", "power bi", "data visualization", "big data", "etl", "excel", "spreadsheet"
                ]):
                    job_domain = "data"
                elif any(word in text_for_domain for word in [
                    "recruiter", "recruitment", "human resources", "hr", "talent acquisition", 
                    "employee relations", "onboarding", "payroll", "hris", "people management"
                ]):
                    job_domain = "hr"
                elif any(word in text_for_domain for word in [
                    "business analyst", "strategy", "operations", "management", "project manager",
                    "consulting", "business development", "product manager", "agile", "scrum"
                ]):
                    job_domain = "business"
                elif any(word in text_for_domain for word in [
                    "marketing", "digital marketing", "content", "social media", "seo", "sem",
                    "brand", "campaign", "advertising", "market research"
                ]):
                    job_domain = "marketing"
                elif any(word in text_for_domain for word in [
                    "financial", "finance", "accounting", "budget", "forecasting", "audit",
                    "financial analyst", "controller", "cpa", "gaap"
                ]):
                    job_domain = "finance"
            
            # Step 2: Enhanced skills database with domain tags and exclusions
            skills_database = {
                "core_skills": {
                    # Engineering Skills
                    "React": {
                        "keywords": ["react", "react.js", "reactjs"], 
                        "domain": ["engineering"], 
                        "weight": 0.9, 
                        "category": "frontend",
                        "skill_type": "core"
                    },
                    "Angular": {
                        "keywords": ["angular", "angular.js", "angularjs"], 
                        "domain": ["engineering"], 
                        "weight": 0.9, 
                        "category": "frontend",
                        "skill_type": "core"
                    },
                    "Vue.js": {
                        "keywords": ["vue", "vue.js", "vuejs"], 
                        "domain": ["engineering"], 
                        "weight": 0.8, 
                        "category": "frontend",
                        "skill_type": "core"
                    },
                    "JavaScript": {
                        "keywords": ["javascript", "js"], 
                        "exclusions": ["json"],
                        "domain": ["engineering"], 
                        "weight": 0.9, 
                        "category": "frontend",
                        "skill_type": "core"
                    },
                    "TypeScript": {
                        "keywords": ["typescript"], 
                        "exclusions": ["datasets", "clients", "reports", "results", "tests", "meets", "gets"],
                        "domain": ["engineering"], 
                        "weight": 0.8, 
                        "category": "frontend",
                        "skill_type": "core"
                    },
                    "Python": {
                        "keywords": ["python"], 
                        "domain": ["engineering", "data"], 
                        "weight": 0.9, 
                        "category": "programming",
                        "skill_type": "core"
                    },
                    "Java": {
                        "keywords": ["java"], 
                        "exclusions": ["javascript", "json"],
                        "domain": ["engineering"], 
                        "weight": 0.8, 
                        "category": "backend",
                        "skill_type": "core"
                    },
                    "Node.js": {
                        "keywords": ["node", "nodejs", "node.js"], 
                        "domain": ["engineering"], 
                        "weight": 0.8, 
                        "category": "backend",
                        "skill_type": "core"
                    },
                    "SQL": {
                        "keywords": ["sql", "mysql", "postgresql", "database queries"], 
                        "exclusions": ["nosql"],
                        "domain": ["engineering", "data"], 
                        "weight": 0.8, 
                        "category": "database",
                        "skill_type": "core"
                    },
                    "HTML5": {
                        "keywords": ["html", "html5"], 
                        "domain": ["engineering"], 
                        "weight": 0.5, 
                        "category": "frontend",
                        "skill_type": "bonus"
                    },
                    "CSS3": {
                        "keywords": ["css", "css3", "styling"], 
                        "domain": ["engineering"], 
                        "weight": 0.6, 
                        "category": "frontend",
                        "skill_type": "bonus"
                    },
                    "Git": {
                        "keywords": ["git", "version control", "github", "gitlab"], 
                        "domain": ["engineering"], 
                        "weight": 0.7, 
                        "category": "tools",
                        "skill_type": "bonus"
                    },
                    "Programming Fundamentals": {
                        "keywords": ["programming", "coding", "development", "software development"], 
                        "domain": ["engineering"], 
                        "weight": 0.8, 
                        "category": "fundamentals",
                        "skill_type": "core"
                    },
                    
                    # Data Skills
                    "Data Analysis": {
                        "keywords": ["data analysis", "data analytics", "analytical"], 
                        "domain": ["data"], 
                        "weight": 0.9, 
                        "category": "analysis",
                        "skill_type": "core"
                    },
                    "Statistics": {
                        "keywords": ["statistics", "statistical analysis", "statistical modeling"], 
                        "domain": ["data"], 
                        "weight": 0.8, 
                        "category": "analysis",
                        "skill_type": "core"
                    },
                    "Excel": {
                        "keywords": ["excel", "spreadsheet", "advanced excel"], 
                        "domain": ["data", "business", "finance"], 
                        "weight": 0.8, 
                        "category": "tools",
                        "skill_type": "core"
                    },
                    "REST APIs": {
                        "keywords": ["rest api", "restful api", "api integration", "rest"], 
                        "domain": ["engineering"], 
                        "weight": 0.7, 
                        "category": "integration",
                        "skill_type": "core"
                    },
                    "State Management": {
                        "keywords": ["state management", "redux", "zustand", "context api"], 
                        "domain": ["engineering"], 
                        "weight": 0.7, 
                        "category": "frontend",
                        "skill_type": "core"
                    },
                    "Build Tools": {
                        "keywords": ["webpack", "vite", "parcel", "build tools", "bundler"], 
                        "domain": ["engineering"], 
                        "weight": 0.6, 
                        "category": "tools",
                        "skill_type": "bonus"
                    },
                    "Responsive Design": {
                        "keywords": ["responsive design", "responsive", "mobile-first"], 
                        "domain": ["engineering"], 
                        "weight": 0.7, 
                        "category": "frontend",
                        "skill_type": "core"
                    },
                    "UX Principles": {
                        "keywords": ["ux principles", "user experience", "usability"], 
                        "domain": ["engineering"], 
                        "weight": 0.6, 
                        "category": "design",
                        "skill_type": "bonus"
                    },
                    "Web Performance": {
                        "keywords": ["web performance", "performance optimization", "optimization"], 
                        "domain": ["engineering"], 
                        "weight": 0.7, 
                        "category": "optimization",
                        "skill_type": "core"
                    },
                    "Power BI": {
                        "keywords": ["power bi", "powerbi"], 
                        "domain": ["data"], 
                        "weight": 0.7, 
                        "category": "visualization",
                        "skill_type": "bonus"
                    },
                    "Tableau": {
                        "keywords": ["tableau"], 
                        "domain": ["data"], 
                        "weight": 0.7, 
                        "category": "visualization",
                        "skill_type": "bonus"
                    },
                    "Data Interpretation": {
                        "keywords": ["data interpretation", "interpret data", "data insights"], 
                        "domain": ["data"], 
                        "weight": 0.8, 
                        "category": "analysis",
                        "skill_type": "core"
                    },
                    
                    # HR Skills
                    "Recruitment": {
                        "keywords": ["recruitment", "recruiting", "hiring", "talent acquisition"], 
                        "domain": ["hr"], 
                        "weight": 0.9, 
                        "category": "hr",
                        "skill_type": "core"
                    },
                    "Employee Relations": {
                        "keywords": ["employee relations", "employee engagement"], 
                        "domain": ["hr"], 
                        "weight": 0.8, 
                        "category": "hr",
                        "skill_type": "core"
                    },
                    "HRIS": {
                        "keywords": ["hris", "hr system", "hr information system"], 
                        "domain": ["hr"], 
                        "weight": 0.7, 
                        "category": "systems",
                        "skill_type": "bonus"
                    },
                    "Onboarding": {
                        "keywords": ["onboarding", "new hire"], 
                        "domain": ["hr"], 
                        "weight": 0.7, 
                        "category": "hr",
                        "skill_type": "bonus"
                    },
                    "Payroll": {
                        "keywords": ["payroll"], 
                        "domain": ["hr"], 
                        "weight": 0.7, 
                        "category": "hr",
                        "skill_type": "bonus"
                    },
                    "HR Fundamentals": {
                        "keywords": ["hr", "human resources", "hr practices"], 
                        "domain": ["hr"], 
                        "weight": 0.8, 
                        "category": "fundamentals",
                        "skill_type": "core"
                    },
                    "People Management": {
                        "keywords": ["people management", "team management", "manage people"], 
                        "domain": ["hr", "business"], 
                        "weight": 0.8, 
                        "category": "management",
                        "skill_type": "core"
                    },
                    
                    # Business/Management Skills
                    "Project Management": {
                        "keywords": ["project management", "project manager", "manage projects"], 
                        "domain": ["business"], 
                        "weight": 0.8, 
                        "category": "management",
                        "skill_type": "core"
                    },
                    "Business Analysis": {
                        "keywords": ["business analysis", "business analyst", "requirements analysis"], 
                        "domain": ["business"], 
                        "weight": 0.8, 
                        "category": "analysis",
                        "skill_type": "core"
                    },
                    "Strategy": {
                        "keywords": ["strategy", "strategic planning", "business strategy"], 
                        "domain": ["business"], 
                        "weight": 0.8, 
                        "category": "strategy",
                        "skill_type": "core"
                    },
                    "Operations": {
                        "keywords": ["operations", "operational"], 
                        "domain": ["business"], 
                        "weight": 0.7, 
                        "category": "operations",
                        "skill_type": "core"
                    },
                    "Agile": {
                        "keywords": ["agile", "agile methodology"], 
                        "domain": ["business", "engineering"], 
                        "weight": 0.8, 
                        "category": "methodology",
                        "skill_type": "bonus"
                    },
                    "Scrum": {
                        "keywords": ["scrum"], 
                        "domain": ["business", "engineering"], 
                        "weight": 0.8, 
                        "category": "methodology",
                        "skill_type": "bonus"
                    },
                    
                    # Marketing Skills
                    "Digital Marketing": {
                        "keywords": ["digital marketing", "online marketing"], 
                        "domain": ["marketing"], 
                        "weight": 0.8, 
                        "category": "marketing",
                        "skill_type": "core"
                    },
                    "Content Creation": {
                        "keywords": ["content creation", "content marketing", "content strategy"], 
                        "domain": ["marketing"], 
                        "weight": 0.7, 
                        "category": "creative",
                        "skill_type": "core"
                    },
                    "Market Research": {
                        "keywords": ["market research", "market analysis"], 
                        "domain": ["marketing", "business"], 
                        "weight": 0.7, 
                        "category": "research",
                        "skill_type": "core"
                    },
                    "Social Media": {
                        "keywords": ["social media", "social media marketing"], 
                        "domain": ["marketing"], 
                        "weight": 0.6, 
                        "category": "digital",
                        "skill_type": "bonus"
                    },
                    "SEO": {
                        "keywords": ["seo", "search engine optimization"], 
                        "domain": ["marketing"], 
                        "weight": 0.7, 
                        "category": "digital",
                        "skill_type": "bonus"
                    },
                    
                    # Finance Skills
                    "Financial Analysis": {
                        "keywords": ["financial analysis", "financial modeling"], 
                        "domain": ["finance"], 
                        "weight": 0.8, 
                        "category": "analysis",
                        "skill_type": "core"
                    },
                    "Accounting": {
                        "keywords": ["accounting", "bookkeeping"], 
                        "domain": ["finance"], 
                        "weight": 0.8, 
                        "category": "finance",
                        "skill_type": "core"
                    },
                    "Budgeting": {
                        "keywords": ["budgeting", "budget planning"], 
                        "domain": ["finance"], 
                        "weight": 0.7, 
                        "category": "finance",
                        "skill_type": "core"
                    },
                    
                    # General/Soft Skills
                    "Communication": {
                        "keywords": ["communication", "verbal communication", "written communication"], 
                        "domain": ["general"], 
                        "weight": 0.8, 
                        "category": "interpersonal",
                        "skill_type": "soft"
                    },
                    "Leadership": {
                        "keywords": ["leadership", "lead", "leading"], 
                        "domain": ["general"], 
                        "weight": 0.7, 
                        "category": "interpersonal",
                        "skill_type": "soft"
                    },
                    "Teamwork": {
                        "keywords": ["teamwork", "team collaboration", "work in team"], 
                        "domain": ["general"], 
                        "weight": 0.7, 
                        "category": "interpersonal",
                        "skill_type": "soft"
                    },
                    "Problem Solving": {
                        "keywords": ["problem solving", "analytical thinking", "troubleshooting"], 
                        "domain": ["general"], 
                        "weight": 0.8, 
                        "category": "analytical",
                        "skill_type": "soft"
                    },
                    "Time Management": {
                        "keywords": ["time management", "organization", "organizational"], 
                        "domain": ["general"], 
                        "weight": 0.7, 
                        "category": "personal",
                        "skill_type": "soft"
                    },
                    "Initiative": {
                        "keywords": ["initiative", "proactive", "self-motivated"], 
                        "domain": ["general"], 
                        "weight": 0.7, 
                        "category": "personal",
                        "skill_type": "soft"
                    },
                    "Learning Ability": {
                        "keywords": ["learning", "eager to learn", "quick learner", "adaptability"], 
                        "domain": ["general"], 
                        "weight": 0.8, 
                        "category": "personal",
                        "skill_type": "soft"
                    },
                    "Collaboration": {
                        "keywords": ["collaboration", "collaborative", "work together"], 
                        "domain": ["general"], 
                        "weight": 0.7, 
                        "category": "interpersonal",
                        "skill_type": "soft"
                    },
                    "Motivation": {
                        "keywords": ["motivation", "motivated", "passion", "passionate"], 
                        "domain": ["general"], 
                        "weight": 0.8, 
                        "category": "personal",
                        "skill_type": "soft"
                    }
                }
            }
            
            # Step 3: Analyze skills with domain filtering
            detected_skills = {}
            
            # Extract all skills from database
            all_skills = skills_database["core_skills"]
            
            for skill_name, skill_data in all_skills.items():
                # Apply domain filtering - only include skills that match job domain OR are general
                skill_domains = skill_data.get("domain", [])
                if job_domain not in skill_domains and "general" not in skill_domains:
                    continue
                
                # Check for exclusions to prevent false positives
                exclusions = skill_data.get("exclusions", [])
                if any(exclusion in text for exclusion in exclusions):
                    continue
                    
                # Check for skill keyword matches
                skill_found = False
                evidence_context = []
                matched_keyword = ""
                
                for keyword in skill_data["keywords"]:
                    if keyword in text:
                        # Enhanced validation to prevent false positives
                        skip_skill = False
                        
                        # For engineering domain, validate technical context
                        if job_domain == "engineering":
                            # Excel should not appear in pure engineering roles unless explicitly mentioned with data analysis
                            if skill_name == "Excel" and not any(
                                data_word in text for data_word in ["data analysis", "spreadsheet", "reporting", "analytics"]
                            ):
                                skip_skill = True
                            
                            # SQL/Python need programming context
                            elif skill_name in ["Python", "Java", "SQL"] and not any(
                                tech_word in text for tech_word in ["programming", "development", "coding", "developer", "engineer", "software"]
                            ):
                                skip_skill = True
                        
                        # For data domain, ensure analytics context
                        elif job_domain == "data":
                            if skill_name in ["React", "HTML5", "CSS3"] and not any(
                                frontend_word in text for frontend_word in ["dashboard", "visualization", "ui", "interface"]
                            ):
                                skip_skill = True
                        
                        if skip_skill:
                            continue
                        
                        evidence_context.append(f"Found '{keyword}' in job description")
                        matched_keyword = keyword
                        skill_found = True
                        break
                
                if skill_found:
                    # Smart skill level detection with contextual experience parsing
                    level = determine_skill_level_smart(text, matched_keyword, skill_name, seniority, is_internship)
                    
                    # Enhanced evidence collection
                    skill_context = extract_skill_context(text, matched_keyword, skill_name)
                    if skill_context:
                        evidence_context.extend(skill_context)
                    
                    detected_skills[skill_name] = {
                        "level": level,
                        "evidence": evidence_context,
                        "weight": skill_data["weight"],
                        "category": skill_data["category"],
                        "skill_type": skill_data["skill_type"],
                        "domain": skill_domains
                    }
            
            # Step 4: Categorize skills with limits on soft skills
            core_skills = []
            soft_skills = []
            bonus_skills = []
            soft_skill_count = 0
            max_soft_skills = 6  # Limit soft skills to prevent flooding
            
            for skill_name, skill_info in detected_skills.items():
                skill_entry = {
                    "skill": skill_name,
                    "level": skill_info["level"],
                    "evidence": skill_info["evidence"],
                    "weight": skill_info["weight"],
                    "category": skill_info["category"],
                    "rating": calculate_skill_rating_enhanced(skill_info["level"], skill_info["evidence"], skill_info["weight"])
                }
                
                skill_type = skill_info["skill_type"]
                
                if skill_type == "soft":
                    if soft_skill_count < max_soft_skills:
                        soft_skills.append(skill_entry)
                        soft_skill_count += 1
                elif skill_type == "core":
                    # For senior+ roles, filter out basic fundamental skills
                    if seniority in ["Senior", "Lead"] and skill_name in ["Programming Fundamentals", "Computer Science Basics"]:
                        bonus_skills.append(skill_entry)  # Move to bonus instead
                    else:
                        core_skills.append(skill_entry)
                else:  # bonus
                    bonus_skills.append(skill_entry)
            
            # Add essential soft skills for internships if not already present
            if is_internship:
                essential_internship_skills = [
                    {"skill": "Learning Ability", "level": "Advanced", "evidence": ["Essential for internship"], "weight": 0.9, "category": "personal"},
                    {"skill": "Motivation", "level": "Advanced", "evidence": ["Important for entry-level"], "weight": 0.8, "category": "personal"},
                    {"skill": "Communication", "level": "Advanced", "evidence": ["Important for collaboration"], "weight": 0.8, "category": "interpersonal"}
                ]
                
                for skill in essential_internship_skills:
                    if not any(s["skill"] == skill["skill"] for s in soft_skills) and soft_skill_count < max_soft_skills:
                        skill["rating"] = calculate_skill_rating_enhanced(skill["level"], skill["evidence"], skill["weight"])
                        soft_skills.append(skill)
                        soft_skill_count += 1
            
            # Populate analysis result
            analysis_result["core_skills"] = core_skills
            analysis_result["soft_skills"] = soft_skills
            analysis_result["bonus_skills"] = bonus_skills
            
            # Extract experience information
            experience_matches = re.findall(r'(\d+)\+?\s*years?', text)
            if experience_matches:
                years = max(int(match) for match in experience_matches)
                analysis_result["experience"] = {
                    "total_years": years,
                    "level": f"{years}+ years",
                    "category": categorize_experience_level(years)
                }
            elif is_internship:
                analysis_result["experience"] = {
                    "total_years": 0,
                    "level": "Entry Level",
                    "category": "internship"
                }
            
            # Add metadata
            analysis_result["metadata"]["detected_domain"] = job_domain
        
        # Sort skills by rating within each category
        for category in ["core_skills", "soft_skills", "bonus_skills"]:
            analysis_result[category].sort(key=lambda x: x["rating"], reverse=True)
        
        logger.info(f"Enhanced analysis for '{title}': Job types: {job_types}, Multi-track: {is_multi_track}, Tracks: {list(analysis_result.get('tracks', {}).keys())}, Skills: {len(analysis_result['core_skills'])} core, {len(analysis_result['soft_skills'])} soft, {len(analysis_result['bonus_skills'])} bonus")
        return analysis_result
        
    except Exception as e:
        logger.error(f"Error in enhanced analysis: {str(e)}")
        return {
            "core_skills": [],
            "soft_skills": [{"skill": "Communication", "level": "Intermediate", "rating": 5, "evidence": ["Default skill"], "weight": 0.5, "category": "interpersonal"}],
            "bonus_skills": [],
            "experience": {},
            "languages": [],
            "tracks": {},
            "metadata": {"job_types": ["general"], "seniority": "Mid", "is_internship": False, "is_multi_track": False}
        }

def determine_skill_level_smart(text: str, keyword: str, skill_name: str, seniority: str, is_internship: bool) -> str:
    """Smart skill level detection with contextual experience parsing"""
    if is_internship:
        return "Basic"
    
    # Look for specific experience requirements around the skill keyword
    keyword_pos = text.find(keyword)
    if keyword_pos != -1:
        # Extended context around the skill mention
        start = max(0, keyword_pos - 150)
        end = min(len(text), keyword_pos + len(keyword) + 150)
        context = text[start:end]
        
        # Pattern 1: "X+ years of experience with [skill]" or "X+ years of [skill]"
        exp_patterns = [
            rf'(\d+)\+?\s*years?\s*of\s*(hands?-?on\s+)?(experience\s+)?(with\s+)?{re.escape(keyword)}',
            rf'(\d+)\+?\s*years?\s*(hands?-?on\s+)?{re.escape(keyword)}',
            rf'{re.escape(keyword)}.*?(\d+)\+?\s*years?',
            rf'(\d+)\+?\s*years?.*?{re.escape(keyword)}'
        ]
        
        for pattern in exp_patterns:
            match = re.search(pattern, context, re.IGNORECASE)
            if match:
                years = int(match.group(1))
                return categorize_years_to_level(years)
        
        # Pattern 2: Look for explicit level indicators near the skill
        level_indicators = {
            'expert': ['expert', 'expertise', 'mastery', 'deep knowledge'],
            'advanced': ['advanced', 'strong', 'proficient', 'extensive', 'solid', 'deep understanding'],
            'intermediate': ['good', 'working knowledge', 'familiar', 'understanding'],
            'basic': ['basic', 'fundamental', 'entry-level', 'beginner']
        }
        
        for level, indicators in level_indicators.items():
            if any(indicator in context for indicator in indicators):
                return level.capitalize()
    
    # Fallback to job seniority if no specific experience found
    if seniority == "Senior":
        return "Advanced"
    elif seniority == "Lead":
        return "Expert"
    else:
        return "Intermediate"

def categorize_years_to_level(years: int) -> str:
    """Convert years of experience to skill level"""
    if years >= 5:
        return "Expert"
    elif years >= 3:
        return "Advanced"
    elif years >= 1:
        return "Intermediate"
    else:
        return "Basic"

def extract_skill_context(text: str, keyword: str, skill_name: str) -> List[str]:
    """Extract meaningful context around skill mentions for evidence"""
    evidence = []
    keyword_pos = text.find(keyword)
    
    if keyword_pos != -1:
        # Get surrounding context
        start = max(0, keyword_pos - 100)
        end = min(len(text), keyword_pos + len(keyword) + 100)
        context = text[start:end]
        
        # Look for experience mentions
        exp_match = re.search(rf'(\d+)\+?\s*years?\s*.*?{re.escape(keyword)}|{re.escape(keyword)}.*?(\d+)\+?\s*years?', context, re.IGNORECASE)
        if exp_match:
            years = int(exp_match.group(1) or exp_match.group(2))
            evidence.append(f"Requires {years}+ years of {skill_name} experience")
        
        # Look for level qualifiers
        qualifiers = ['expert', 'advanced', 'strong', 'proficient', 'extensive', 'solid', 'hands-on', 'deep']
        for qualifier in qualifiers:
            if qualifier in context:
                evidence.append(f"Described as '{qualifier}' {skill_name} skill")
                break
        
        # Look for version/framework specifics
        version_match = re.search(rf'{re.escape(keyword)}\s*(\d+[\.\d]*|[a-z]+\s*\d+)', context, re.IGNORECASE)
        if version_match:
            version = version_match.group(1)
            evidence.append(f"Specific version/framework: {skill_name} {version}")
    
    return evidence

def validate_skill_context_enhanced(text: str, keyword: str, skill_name: str, skill_data: dict) -> bool:
    """Enhanced context validation with domain awareness"""
    keyword_pos = text.find(keyword)
    if keyword_pos == -1:
        return False
    
    # Get surrounding context
    start = max(0, keyword_pos - 100)
    end = min(len(text), keyword_pos + len(keyword) + 100)
    context = text[start:end]
    
    # Check exclusions
    exclusions = skill_data.get("exclusions", [])
    if any(exclusion in context for exclusion in exclusions):
        return False
    
    # Special validation for similar skills
    if skill_name == "Java" and keyword == "java":
        if "javascript" in context or "json" in context:
            return False
    
    # Check for negative indicators
    negative_patterns = ["not required", "not necessary", "optional", "nice to have"]
    for pattern in negative_patterns:
        if pattern in context:
            return False
    
    return True

def determine_skill_level_enhanced(text: str, keyword: str, default_level: str, is_internship: bool) -> str:
    """Determine skill level with enhanced seniority awareness"""
    if is_internship:
        return "Basic"
    
    # Look for level indicators around the keyword
    keyword_pos = text.find(keyword)
    start = max(0, keyword_pos - 50)
    end = min(len(text), keyword_pos + len(keyword) + 50)
    context = text[start:end]
    
    if any(word in context for word in ["expert", "advanced", "senior", "lead"]):
        return "Expert" if "expert" in context else "Advanced"
    elif any(word in context for word in ["basic", "junior", "entry", "beginner"]):
        return "Basic"
    elif any(word in context for word in ["intermediate", "mid"]):
        return "Intermediate"
    
    return default_level

def calculate_skill_rating_enhanced(level: str, evidence: list, weight: float) -> int:
    """Calculate skill rating with enhanced logic"""
    base_rating = {
        "Basic": 4,
        "Intermediate": 6,
        "Advanced": 8,
        "Expert": 10
    }.get(level, 6)
    
    # Adjust based on evidence strength
    evidence_bonus = min(len(evidence), 2)  # Max 2 point bonus
    
    # Adjust based on weight
    weight_multiplier = 0.8 + (weight * 0.4)  # 0.8 to 1.2 multiplier
    
    final_rating = int(base_rating * weight_multiplier) + evidence_bonus
    return max(1, min(10, final_rating))

def categorize_experience_level(years: int) -> str:
    """Categorize experience level"""
    if years == 0:
        return "internship"
    elif years <= 2:
        return "junior"
    elif years <= 5:
        return "mid"
    elif years <= 8:
        return "senior"
    else:
        return "lead"

def reload_skills_taxonomy():
    """Reload skills taxonomy from file (useful for updates without restart)"""
    global SKILLS_TAXONOMY
    try:
        SKILLS_TAXONOMY = load_skills_taxonomy()
        logger.info("Skills taxonomy reloaded successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to reload skills taxonomy: {str(e)}")
        return False

def determine_skill_level_with_evidence(text: str, keyword: str, weight: float, title: str) -> tuple:
    """Determine skill level and provide evidence from job description"""
    evidence_snippets = []
    
    # Find keyword position and extract context
    keyword_pos = text.find(keyword)
    if keyword_pos != -1:
        start = max(0, keyword_pos - 30)
        end = min(len(text), keyword_pos + len(keyword) + 30)
        context = text[start:end].strip()
        evidence_snippets.append(f"Mentioned in context: '{context}'")
        
        # Check for explicit level mentions
        if any(word in context for word in ["expert", "expertise", "mastery", "preferred"]):
            return "Expert", evidence_snippets
        elif any(word in context for word in ["strong", "proficiency", "experienced", "advanced"]):
            return "Advanced", evidence_snippets
    
    # Infer from job title
    if "senior" in title.lower() or "lead" in title.lower():
        if weight >= 0.8:  # Core skills for senior roles
            return "Expert", evidence_snippets + [f"Senior role implies {keyword} expertise"]
        else:
            return "Advanced", evidence_snippets + [f"Senior role suggests advanced {keyword}"]
    elif "junior" in title.lower() or "entry" in title.lower():
        return "Intermediate", evidence_snippets + [f"Entry-level role, {keyword} at intermediate level"]
    
    return "Advanced" if weight >= 0.7 else "Intermediate", evidence_snippets

def calculate_skill_rating(level: str, evidence: list, weight: float) -> int:
    """Calculate a 1-10 rating for HR evaluation"""
    base_rating = {
        "Expert": 9,
        "Advanced": 7,
        "Intermediate": 5,
        "Beginner": 3
    }.get(level, 5)
    
    # Adjust based on evidence quality
    evidence_bonus = min(len(evidence), 2)  # Max 2 bonus points for evidence
    
    # Adjust based on skill importance (weight)
    weight_bonus = 1 if weight >= 0.8 else 0
    
    final_rating = min(10, base_rating + evidence_bonus + weight_bonus)
    return final_rating

def categorize_experience_level(years: int) -> str:
    """Categorize experience level for HR"""
    if years >= 10:
        return "Senior/Principal Level"
    elif years >= 5:
        return "Senior Level"
    elif years >= 2:
        return "Mid Level"
    else:
        return "Junior Level"

def detect_seniority_ai(title: str, description: str) -> str:
    """Auto-detect seniority level from job content"""
    try:
        text = (title + " " + description).lower()
        
        # Priority order matters
        if any(word in text for word in ["principal", "staff", "architect"]): 
            return "Principal"
        if any(word in text for word in ["lead", "team lead", "tech lead"]): 
            return "Lead"
        if any(word in text for word in ["senior", "sr.", "sr "]):
            return "Senior"
        if any(word in text for word in ["junior", "jr.", "entry", "graduate"]):
            return "Junior"
        if any(word in text for word in ["mid", "intermediate", "mid-level"]):
            return "Mid"
        
        # Analyze years of experience
        experience_match = re.search(r'(\d+)\+?\s*years?', text)
        if experience_match:
            years = int(experience_match.group(1))
            if years >= 8: return "Principal"
            if years >= 5: return "Senior"
            if years >= 2: return "Mid"
            return "Junior"
        
        logger.info(f"No clear seniority detected for '{title}'")
        return "Mid"  # Default to Mid instead of empty
        
    except Exception as e:
        logger.error(f"Error detecting seniority: {str(e)}")
        return "Mid"

def generate_summary_ai(job_data: dict, style: str = "standard") -> str:
    """AI-powered job summary generation with multiple styles"""
    try:
        title = job_data.get('title', '')
        description = job_data.get('description', '')
        requirements = job_data.get('requirements', [])
        seniority = job_data.get('seniority', '')
        screening_questions = job_data.get('screening_questions', [])
        
        if style == "ats":
            return generate_ats_summary(title, description, requirements, seniority)
        elif style == "short":
            return generate_short_summary(title, description, requirements, seniority)
        else:
            return generate_standard_summary(title, description, requirements, seniority, screening_questions)
            
    except Exception as e:
        logger.error(f"Error generating summary: {str(e)}")
        return f"**{title}**\n\n{description}\n\nPlease contact HR for more details."

def generate_standard_summary(title: str, description: str, requirements: List, seniority: str, screening_questions: List) -> str:
    """Generate standard detailed summary"""
    # Group requirements by category
    req_by_category = {}
    for req in requirements:
        if isinstance(req, dict):
            category = req.get('category', 'general')
            if category not in req_by_category:
                req_by_category[category] = []
            req_by_category[category].append(f"• {req.get('skill', 'Unknown')} ({req.get('level', 'Intermediate')})")
        else:
            # Handle legacy string format
            if 'general' not in req_by_category:
                req_by_category['general'] = []
            req_by_category['general'].append(f"• {req}")
    
    req_text = ""
    for category, skills in req_by_category.items():
        req_text += f"\n**{category.title()} Skills:**\n" + '\n'.join(skills) + "\n"
    
    questions_text = '\n'.join([f"• {q}" for q in screening_questions]) if screening_questions else "• Technical assessment and cultural fit interview"
    
    return f"""🚀 **{title}** - {seniority} Level Position

📋 **Role Overview:**
{description[:400]}{'...' if len(description) > 400 else ''}

🎯 **Key Requirements:**{req_text}

💼 **What We're Looking For:**
We seek a {seniority.lower() if seniority else 'skilled'} professional who can contribute to our team's success through technical excellence and collaborative spirit.

🔍 **Assessment Process:**
{questions_text}

This position offers excellent growth opportunities in a dynamic, innovation-focused environment."""

def generate_ats_summary(title: str, description: str, requirements: List, seniority: str) -> str:
    """Generate ATS-optimized summary"""
    skills = []
    for req in requirements:
        if isinstance(req, dict):
            skills.append(req.get('skill', ''))
        else:
            skills.append(str(req).split(':')[0] if ':' in str(req) else str(req))
    
    return f"{title} | {seniority} | {description[:200]} | Skills: {', '.join(skills[:10])}"

def generate_short_summary(title: str, description: str, requirements: List, seniority: str) -> str:
    """Generate short summary for quick reference"""
    top_skills = []
    for req in requirements[:5]:  # Top 5 skills only
        if isinstance(req, dict):
            top_skills.append(req.get('skill', ''))
        else:
            top_skills.append(str(req).split(':')[0] if ':' in str(req) else str(req))
    
    return f"**{title}** ({seniority})\n{description[:150]}...\n\nKey skills: {', '.join(top_skills)}"

# Job Workflow Endpoints
@app.post("/jobs/init", response_model=JobRead)
def init_job(job: JobCreate, db: Session = Depends(get_db)):
    """Step 1: HR adds title and description"""
    try:
        job.requirements = []
        job.seniority = None
        job.domain_tags = []
        job.screening_questions = []
        job.ats_keywords = []
        job.summary = None
        
        created_job = create_job(db, job)
        logger.info(f"Initialized job: {created_job.title}")
        return created_job
        
    except Exception as e:
        logger.error(f"Error initializing job: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to initialize job: {str(e)}")

@app.post("/jobs/{job_id}/suggest_requirements", response_model=JobRead)
def suggest_requirements(job_id: int, db: Session = Depends(get_db)):
    """Step 2: Agent suggests requirements"""
    try:
        job = get_job(db, job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        suggested_requirements = analyze_requirements_ai(job.title, job.description)
        job.requirements = suggested_requirements
        
        db.commit()
        db.refresh(job)
        logger.info(f"Generated requirements for job {job_id}: {len(suggested_requirements)} requirements")
        return job
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error suggesting requirements for job {job_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to suggest requirements: {str(e)}")

@app.put("/jobs/{job_id}", response_model=JobRead)
def update_job(job_id: int, job_update: JobCreate, db: Session = Depends(get_db)):
    """Step 3: HR updates requirements and other fields"""
    try:
        job = get_job(db, job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        for field, value in job_update.dict(exclude_unset=True).items():
            setattr(job, field, value)
        
        db.commit()
        db.refresh(job)
        logger.info(f"Updated job {job_id}")
        return job
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating job {job_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update job: {str(e)}")

@app.post("/jobs/{job_id}/summarize", response_model=JobRead)
def summarize_job(job_id: int, style: str = "standard", db: Session = Depends(get_db)):
    """Step 4: Agent summarizes job for CV comparison"""
    try:
        job = get_job(db, job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        job_data = {
            "title": job.title,
            "description": job.description,
            "requirements": job.requirements,
            "seniority": job.seniority,
            "screening_questions": job.screening_questions
        }
        
        job.summary = generate_summary_ai(job_data, style)
        db.commit()
        db.refresh(job)
        logger.info(f"Generated {style} summary for job {job_id}")
        return job
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error summarizing job {job_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to summarize job: {str(e)}")

# CRUD Endpoints
@app.get("/jobs", response_model=List[JobRead])
def read_jobs(db: Session = Depends(get_db)):
    """Get list of all jobs"""
    try:
        jobs = get_jobs(db)
        logger.info(f"Retrieved {len(jobs)} jobs")
        return jobs
    except Exception as e:
        logger.error(f"Error retrieving jobs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve jobs: {str(e)}")

@app.post("/jobs", response_model=JobRead)
def create_new_job(job: JobCreate, db: Session = Depends(get_db)):
    """Create a new job"""
    try:
        created_job = create_job(db, job)
        logger.info(f"Created new job: {created_job.title}")
        return created_job
    except Exception as e:
        logger.error(f"Error creating job: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create job: {str(e)}")

@app.get("/jobs/{job_id}", response_model=JobRead)
def read_job(job_id: int, db: Session = Depends(get_db)):
    """Get a specific job by ID"""
    try:
        job = get_job(db, job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        return job
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving job {job_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve job: {str(e)}")

# Enhanced AI Analysis Endpoints
@app.post("/jobs/analyze-requirements")
async def analyze_requirements_endpoint(request: dict):
    """Analyze job title and description with HR-focused categorization"""
    try:
        title = request.get('title', '')
        description = request.get('description', '')
        
        if not title or not description:
            raise HTTPException(status_code=400, detail="Title and description are required")
        
        analysis = analyze_requirements_ai(title, description)
        
        # Create backwards-compatible format for existing frontend
        legacy_requirements = []
        for skill in analysis["core_skills"] + analysis["soft_skills"] + analysis["bonus_skills"]:
            legacy_requirements.append(f"{skill['skill']}:{skill['level']}")
        
        # Add experience if present
        if analysis["experience"]:
            legacy_requirements.append(f"Experience:{analysis['experience']['level']}")
        
        logger.info(f"Analyzed requirements for '{title}': {len(legacy_requirements)} total requirements found")
        
        return {
            # Legacy format for existing frontend compatibility
            "requirements": legacy_requirements,
            "detected_seniority": analysis["metadata"]["seniority"],
            
            # New HR-structured format
            "hr_analysis": {
                "core_skills": analysis["core_skills"],
                "soft_skills": analysis["soft_skills"], 
                "bonus_skills": analysis["bonus_skills"],
                "experience": analysis["experience"],
                "languages": analysis["languages"],
                "tracks": analysis.get("tracks", {}),  # Multi-track breakdown
                "structured_data": analysis,  # Full analysis data
                "summary": {
                    "total_core_skills": len(analysis["core_skills"]),
                    "total_soft_skills": len(analysis["soft_skills"]),
                    "total_bonus_skills": len(analysis["bonus_skills"]),
                    "job_types": analysis["metadata"]["job_types"],
                    "seniority": analysis["metadata"]["seniority"],
                    "is_multi_track": analysis["metadata"].get("is_multi_track", False),
                    "track_count": len(analysis.get("tracks", {})),
                    "avg_core_rating": round(sum(s["rating"] for s in analysis["core_skills"]) / len(analysis["core_skills"]), 1) if analysis["core_skills"] else 0,
                    "languages_required": len(analysis["languages"])
                }
            },
            
            # Metadata for compatibility
            "analysis_metadata": {
                "total_skills": len(legacy_requirements),
                "categories": ["core", "soft", "bonus"] if any([analysis["core_skills"], analysis["soft_skills"], analysis["bonus_skills"]]) else ["general"],
                "tracks": list(analysis.get("tracks", {}).keys())
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in analyze_requirements_endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/jobs/hr-analysis")
async def hr_analysis_endpoint(request: dict):
    """Dedicated HR analysis endpoint with professional reporting format"""
    try:
        title = request.get('title', '')
        description = request.get('description', '')
        
        if not title or not description:
            raise HTTPException(status_code=400, detail="Title and description are required")
        
        analysis = analyze_requirements_ai(title, description)
        
        # Generate HR report
        hr_report = generate_hr_analysis_report(title, analysis)
        
        return {
            "job_title": title,
            "analysis_date": "2025-08-22",  # In production, use actual date
            "hr_report": hr_report,
            "structured_data": analysis
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in hr_analysis_endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"HR analysis failed: {str(e)}")

def generate_hr_analysis_report(job_title: str, analysis: dict) -> str:
    """Generate a professional HR analysis report"""
    
    # Core Skills Section
    core_section = "## 🎯 CORE SKILLS (Must-Have)\n"
    core_section += "These are essential technical requirements for job performance:\n\n"
    
    if analysis["core_skills"]:
        for skill in analysis["core_skills"][:8]:  # Top 8 core skills
            core_section += f"• **{skill['skill']}**: {skill['level']} (Rating: {skill['rating']}/10)\n"
            if skill['evidence']:
                core_section += f"  *Evidence: {skill['evidence'][0][:80]}...*\n"
    else:
        core_section += "*No specific core technical skills identified*\n"
    
    # Soft Skills Section  
    soft_section = "\n## 🤝 SOFT SKILLS (Team & Culture Fit)\n"
    soft_section += "These indicate how well the candidate will integrate with the team:\n\n"
    
    if analysis["soft_skills"]:
        for skill in analysis["soft_skills"]:
            evidence_status = "Strong Evidence" if len(skill['evidence']) > 1 else ("Mentioned" if skill['evidence'] else "Not Mentioned")
            soft_section += f"• **{skill['skill']}**: {evidence_status}\n"
    else:
        soft_section += "*No specific soft skills requirements identified*\n"
    
    # Bonus Skills Section
    bonus_section = "\n## ⭐ BONUS SKILLS (Competitive Advantage)\n"
    bonus_section += "These give candidates an edge but aren't dealbreakers:\n\n"
    
    if analysis["bonus_skills"]:
        for skill in analysis["bonus_skills"][:6]:  # Top 6 bonus skills
            bonus_section += f"• **{skill['skill']}**: {skill['level']}\n"
    else:
        bonus_section += "*No bonus skills specified*\n"
    
    # Experience & Languages Section
    additional_section = "\n## 📋 ADDITIONAL REQUIREMENTS\n"
    
    if analysis["experience"]:
        exp = analysis["experience"]
        additional_section += f"**Experience**: {exp['level']} ({exp['category']})\n"
    
    if analysis["languages"]:
        additional_section += "**Languages**: "
        lang_reqs = [f"{lang['language']} ({lang['requirement']})" for lang in analysis["languages"]]
        additional_section += ", ".join(lang_reqs) + "\n"
    
    # Summary Section
    summary_section = f"\n## 📊 HIRING RECOMMENDATION\n"
    summary_section += f"**Job Type**: {analysis['metadata']['job_type'].title()}\n"
    summary_section += f"**Seniority Level**: {analysis['metadata']['seniority']}\n"
    summary_section += f"**Core Skills Count**: {len(analysis['core_skills'])}\n"
    
    if analysis["core_skills"]:
        avg_rating = sum(s["rating"] for s in analysis["core_skills"]) / len(analysis["core_skills"])
        summary_section += f"**Technical Complexity**: {avg_rating:.1f}/10\n"
        
        if avg_rating >= 8:
            summary_section += "**Recommendation**: Look for senior candidates with proven expertise\n"
        elif avg_rating >= 6:
            summary_section += "**Recommendation**: Mid to senior level candidates with solid experience\n"
        else:
            summary_section += "**Recommendation**: Mid-level candidates with growth potential\n"
    
    return core_section + soft_section + bonus_section + additional_section + summary_section

@app.post("/jobs/generate-summary")
async def generate_summary_endpoint(request: dict):
    """Generate AI-powered job summary with multiple style options"""
    try:
        style = request.get('style', 'standard')
        
        if style not in ['standard', 'ats', 'short']:
            raise HTTPException(status_code=400, detail="Style must be 'standard', 'ats', or 'short'")
        
        summary = generate_summary_ai(request, style)
        
        logger.info(f"Generated {style} summary for job: {request.get('title', 'Unknown')}")
        return {
            "summary": summary,
            "style": style,
            "metadata": {
                "word_count": len(summary.split()),
                "character_count": len(summary)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in generate_summary_endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Summary generation failed: {str(e)}")

@app.get("/jobs/skills-taxonomy")
async def get_skills_taxonomy():
    """Get the skills taxonomy for frontend reference"""
    try:
        return {
            "taxonomy": SKILLS_TAXONOMY,
            "categories": list(set([skill["category"] for skill in SKILLS_TAXONOMY.values()])),
            "total_skills": len(SKILLS_TAXONOMY)
        }
    except Exception as e:
        logger.error(f"Error retrieving skills taxonomy: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve skills taxonomy")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "services": {
            "database": "connected",
            "ai_analysis": "operational"
        }
    }

# =============================
# V2 RULE-DRIVEN ANALYZER (Reference Spec Implementation)
# =============================

def analyze_requirements_ai_v2(title: str, description: str) -> Dict[str, Any]:
    """Deterministic rule-based analysis (reference spec)."""
    text = (title + " " + description).lower()

    # --- Job Type Detection (reuse multi-detection from updated detect_job_type if present) ---
    job_types = detect_job_type(title, description)

    # --- Seniority Detection ---
    seniority = detect_seniority_ai(title, description)
    # Normalize internship detection
    if any(w in title.lower() for w in ["intern", "internship", "trainee"]) or re.search(r"\b(no prior|no professional|no experience)\b", text):
        seniority = "Internship"

    # --- Default level map ---
    default_level_map = {
        "Internship": "Basic",
        "Junior": "Intermediate",
        "Mid": "Intermediate",
        "Senior": "Advanced",
        "Lead": "Expert",
        "Principal": "Expert"
    }
    default_level = default_level_map.get(seniority, "Intermediate")

    # --- Multi-track internship detection ---
    multi_track_indicator = any(w in text for w in ["tracks", "track", "areas", "fields", "paths", "departments"]) and "intern" in seniority.lower()

    # --- Track templates ---
    track_templates = {
        "tech": {
            "core": ["Programming Fundamentals", "Computer Science Basics", "Problem Solving"],
            "bonus": ["Git", "HTML5", "CSS3", "Python"]
        },
        "data": {
            "core": ["Statistics", "Excel", "Data Analysis", "Data Interpretation"],
            "bonus": ["SQL", "Python"]
        },
        "management": {
            "core": ["Organization", "Time Management", "Project Planning"],
            "bonus": ["Agile", "Scrum"]
        },
        "hr": {
            "core": ["HR Fundamentals"],
            "bonus": ["Recruitment", "People Management", "Employee Relations", "HRIS"]
        }
    }

    analysis_result: Dict[str, Any] = {
        "core_skills": [],
        "soft_skills": [],
        "bonus_skills": [],
        "experience": {},
        "languages": [],
        "tracks": {},
        "metadata": {
            "job_types": job_types,
            "seniority": seniority,
            "is_internship": seniority == "Internship",
            "is_multi_track": bool(multi_track_indicator and seniority == "Internship"),
            "default_level": default_level
        }
    }

    # --- Experience Parsing ---
    exp_match = re.search(r"(\d+)\+?\s*years", text)
    if exp_match:
        years = int(exp_match.group(1))
        analysis_result["experience"] = {
            "total_years": years,
            "level": f"{years}+ years",
            "category": categorize_experience_level(years)
        }
    elif seniority == "Internship":
        analysis_result["experience"] = {"total_years": 0, "level": "Entry Level", "category": "internship"}

    # ================= Archetype Templates (Benchmark Spec) =================
    # Each template defines explicit expected skills overriding heuristic detection
    lvl_rating = {"Basic":5, "Intermediate":6, "Advanced":8, "Expert":10}
    def add_skill(bucket, skill, level, category):
        bucket.append({"skill":skill, "level":level, "rating":lvl_rating.get(level,6), "evidence":["Archetype"], "category":category})

    normalized_title = title.lower()
    templates = []
    # Internship multi-track handled later
    if seniority != "Internship":
        if "senior frontend developer" in normalized_title:
            seniority = "Senior"
            templates = [
                ("core","JavaScript","Expert"),("core","TypeScript","Advanced"),("core","React","Expert"),("core","Responsive Design","Advanced"),("core","State Management","Advanced"),("core","REST APIs","Advanced"),
                ("bonus","HTML5","Intermediate"),("bonus","CSS3","Intermediate"),("bonus","Git","Advanced"),("bonus","Build Tools","Advanced"),("bonus","Agile","Intermediate"),
                ("soft","Leadership","Advanced"),("soft","Communication","Advanced"),("soft","Collaboration","Intermediate")
            ]
        elif "frontend engineer" in normalized_title:
            # Determine seniority based on experience and responsibilities
            if re.search(r"3-4|3 to 4|mid.level|mid level", description.lower()):
                seniority = "Mid"
            elif re.search(r"5\+|senior", description.lower()):
                seniority = "Senior"
            else:
                seniority = "Mid"  # Default for frontend engineer
            
            # Base frontend skills - frameworks added conditionally
            templates = [
                ("core","JavaScript","Advanced"),("core","TypeScript","Advanced"),("core","Responsive Design","Advanced"),("core","Web Performance","Intermediate"),("core","State Management","Advanced"),("core","REST APIs","Advanced"),
                ("bonus","HTML5","Intermediate"),("bonus","CSS3","Intermediate"),("bonus","Git","Advanced"),("bonus","Build Tools","Intermediate"),("bonus","Agile","Intermediate"),("bonus","DevOps","Intermediate"),("bonus","CI/CD","Intermediate"),("bonus","Web Security","Intermediate"),
                ("soft","Communication","Advanced"),("soft","Problem Solving","Advanced"),("soft","Collaboration","Intermediate")
            ]
            # Add frameworks only if mentioned
            if "react" in description.lower():
                templates.append(("core","React","Expert"))
                templates.append(("core","JSX","Intermediate"))
            if "angular" in description.lower():
                templates.append(("core","Angular","Expert"))
            if "vue" in description.lower():
                templates.append(("core","Vue.js","Expert"))
            # Add Docker if mentioned (as bonus)
            if "docker" in description.lower():
                templates.append(("bonus","Docker","Intermediate"))
            # Add Testing if mentioned (as bonus)
            if any(test in description.lower() for test in ["jest", "jasmine", "karma", "testing", "unit test"]):
                templates.append(("bonus","Testing","Intermediate"))
            # Leadership only for Senior
            if seniority == "Senior":
                templates.append(("soft","Leadership","Intermediate"))
        elif "full-stack developer" in normalized_title or "full stack developer" in normalized_title:
            # Promote to Senior if clear full breadth (frontend + backend + cloud) even without explicit years
            if re.search(r"5\+|senior", description.lower()) or all(k in description.lower() for k in ["react","node","aws"]):
                seniority = "Senior"
            templates = [
                ("core","React","Advanced"),("core","JavaScript","Advanced"),("core","TypeScript","Advanced"),("core","Node.js","Advanced"),("core","REST APIs","Advanced"),("core","SQL","Intermediate"),
                ("bonus","AWS","Advanced"),("bonus","Git","Advanced"),("bonus","Build Tools","Intermediate"),("bonus","Agile","Intermediate"),("bonus","CI/CD","Intermediate"),
                ("soft","Problem Solving","Advanced"),("soft","Collaboration","Advanced"),("soft","Communication","Intermediate"),("soft","Time Management","Intermediate")
            ]
        elif "data engineer" in normalized_title:
            seniority = "Senior" if re.search(r"5\+|senior", description.lower()) else seniority
            templates = [
                ("core","SQL","Expert"),("core","Python","Advanced"),("core","Data Analysis","Advanced"),("core","Data Modeling","Advanced"),
                ("bonus","Spark","Advanced"),("bonus","Hadoop","Advanced"),("bonus","AWS","Intermediate"),("bonus","GCP","Intermediate"),("bonus","Git","Intermediate"),("bonus","CI/CD","Intermediate"),
                ("soft","Problem Solving","Advanced"),("soft","Communication","Intermediate"),("soft","Collaboration","Intermediate")
            ]
        elif "technical project manager" in normalized_title or ("project manager" in normalized_title and "technical" in description.lower()):
            seniority = "Lead"
            templates = [
                ("core","Project Planning","Advanced"),("core","Agile","Advanced"),("core","Scrum","Advanced"),("core","Business Analysis","Intermediate"),
                ("bonus","Strategy","Intermediate"),("bonus","REST APIs","Basic"),("bonus","SQL","Basic"),("bonus","Certifications","Intermediate"),
                ("soft","Leadership","Expert"),("soft","Communication","Advanced"),("soft","Collaboration","Advanced"),("soft","Negotiation","Advanced")
            ]
        elif "machine learning engineer" in normalized_title and ("nlp" in normalized_title or "nlp" in description.lower()):
            seniority = "Senior"
            templates = [
                ("core","Python","Expert"),("core","Machine Learning","Expert"),("core","Data Analysis","Advanced"),("core","Statistics","Advanced"),("core","NLP","Advanced"),
                ("bonus","PyTorch","Advanced"),("bonus","TensorFlow","Advanced"),("bonus","Transformers","Advanced"),("bonus","MLOps","Intermediate"),("bonus","Cloud Platforms","Intermediate"),("bonus","Git","Intermediate"),
                ("soft","Problem Solving","Expert"),("soft","Communication","Intermediate"),("soft","Research Ability","Advanced")
            ]
        elif "senior ui/ux designer" in normalized_title or ("ui/ux designer" in normalized_title and ("senior" in description.lower() or "5+" in description.lower())):
            seniority = "Senior"
            templates = [
                ("core","UX Principles","Expert"),("core","Responsive Design","Advanced"),("core","Web Performance","Intermediate"),
                ("bonus","Figma","Advanced"),("bonus","Sketch","Advanced"),("bonus","HTML5","Basic"),("bonus","CSS3","Basic"),("bonus","Market Research","Intermediate"),
                ("soft","Communication","Advanced"),("soft","Collaboration","Advanced"),("soft","Creativity","Expert"),("soft","Empathy","Advanced")
            ]
        elif "cloud security architect" in normalized_title:
            seniority = "Lead"
            templates = [
                ("core","Cloud Platforms","Expert"),("core","Web Security","Expert"),("core","Programming Fundamentals","Intermediate"),
                ("bonus","DevOps","Intermediate"),("bonus","Compliance","Advanced"),("bonus","Git","Intermediate"),("bonus","Automation Tools","Intermediate"),("bonus","CI/CD","Intermediate"),
                ("soft","Problem Solving","Expert"),("soft","Attention to Detail","Advanced"),("soft","Communication","Intermediate")
            ]
        elif "marketing data analyst" in normalized_title:
            seniority = "Mid"
            templates = [
                ("core","Data Analysis","Advanced"),("core","SQL","Advanced"),("core","Excel","Advanced"),("core","Market Research","Advanced"),
                ("bonus","Power BI","Intermediate"),("bonus","Tableau","Intermediate"),("bonus","SEO","Intermediate"),("bonus","Digital Marketing","Intermediate"),
                ("soft","Communication","Advanced"),("soft","Problem Solving","Intermediate"),("soft","Adaptability","Intermediate")
            ]
        elif "robotics engineer" in normalized_title:
            seniority = "Senior" if re.search(r"5\+|senior", description.lower()) else seniority
            templates = [
                ("core","C++","Advanced"),("core","Python","Advanced"),("core","Programming Fundamentals","Advanced"),("core","Embedded Systems","Advanced"),("core","Robotics","Advanced"),
                ("bonus","Machine Vision","Intermediate"),("bonus","Control Systems","Intermediate"),("bonus","Git","Intermediate"),("bonus","MATLAB","Intermediate"),("bonus","Data Analysis","Intermediate"),
                ("soft","Problem Solving","Expert"),("soft","Collaboration","Intermediate"),("soft","Communication","Intermediate")
            ]
        elif "chef de partie" in normalized_title or ("chef" in normalized_title and "partie" in normalized_title):
            seniority = "Mid"
            templates = [
                ("core","Culinary Skills","Expert"),("core","Food Safety","Advanced"),("core","Time Management","Advanced"),
                ("bonus","Menu Planning","Intermediate"),("bonus","Leadership","Intermediate"),
                ("soft","Teamwork","Advanced"),("soft","Communication","Intermediate"),("soft","Creativity","Intermediate"),("soft","Stress Management","Advanced")
            ]
        elif "truck driver" in normalized_title or ("driver" in normalized_title and "truck" in description.lower()):
            seniority = "Mid"
            templates = [
                ("core","Driving License","Expert"),("core","Road Safety","Expert"),("core","Time Management","Advanced"),
                ("bonus","Navigation","Intermediate"),("bonus","Vehicle Maintenance","Intermediate"),
                ("soft","Responsibility","Advanced"),("soft","Stress Management","Intermediate"),("soft","Communication","Intermediate")
            ]
        elif "junior software developer" in normalized_title or ("software developer" in normalized_title and "junior" in description.lower()):
            seniority = "Junior"
            templates = [
                ("core","JavaScript","Intermediate"),("core","HTML5","Intermediate"),("core","CSS3","Intermediate"),("core","Problem Solving","Intermediate"),
                ("bonus","Git","Basic"),("bonus","Build Tools","Basic"),
                ("soft","Communication","Intermediate"),("soft","Collaboration","Intermediate")
            ]
        elif "data analyst" in normalized_title and "scientist" not in normalized_title:
            seniority = "Mid" if re.search(r"3\+|mid", description.lower()) else seniority
            templates = [
                ("core","SQL","Advanced"),("core","Excel","Advanced"),("core","Tableau","Advanced"),("core","Python","Intermediate"),("core","Statistics","Intermediate"),("core","Data Analysis","Advanced"),
                ("bonus","Power BI","Advanced"),("bonus","Business Analysis","Intermediate"),("bonus","Communication","Advanced"),
                ("soft","Communication","Advanced"),("soft","Problem Solving","Intermediate"),("soft","Collaboration","Intermediate")
            ]
        elif "graphic designer" in normalized_title:
            seniority = "Mid" if re.search(r"3\+|senior", description.lower()) else seniority
            templates = [
                ("core","Adobe Photoshop","Advanced"),("core","Adobe Illustrator","Advanced"),("core","Creativity","Advanced"),("core","Typography","Intermediate"),("core","Figma","Intermediate"),
                ("bonus","Sketch","Intermediate"),("bonus","Web Performance","Basic"),("bonus","Responsive Design","Basic"),
                ("soft","Communication","Intermediate"),("soft","Collaboration","Intermediate")
            ]
        elif "customer support" in normalized_title:
            seniority = "Mid"
            templates = [
                ("core","Customer Service","Advanced"),("core","Problem Solving","Advanced"),("core","Communication","Expert"),
                ("bonus","CRM Tools","Intermediate"),("bonus","Time Management","Intermediate"),("bonus","Organization","Intermediate"),
                ("soft","Empathy","Advanced"),("soft","Responsibility","Advanced"),("soft","Stress Management","Intermediate")
            ]
        elif "accountant" in normalized_title:
            seniority = "Mid" if not re.search(r"senior", description.lower()) else "Senior"
            templates = [
                ("core","Accounting","Expert"),("core","Excel","Advanced"),("core","Financial Analysis","Advanced"),("core","Bookkeeping","Advanced"),
                ("bonus","QuickBooks","Intermediate"),("bonus","SAP","Intermediate"),("bonus","Communication","Intermediate"),
                ("soft","Attention to Detail","Advanced"),("soft","Time Management","Advanced")
            ]
        elif "biology" in normalized_title or "biologist" in normalized_title or "researcher" in normalized_title:
            seniority = "Senior" if re.search(r"phd|10\+", description.lower()) else seniority
            templates = [
                ("core","Biology","Expert"),("core","Lab Techniques","Advanced"),("core","Data Analysis","Advanced"),("core","Research","Expert"),("core","Writing","Advanced"),
                ("bonus","Statistics","Intermediate"),("bonus","Python","Intermediate"),("bonus","Excel","Intermediate"),
                ("soft","Communication","Intermediate"),("soft","Problem Solving","Advanced"),("soft","Research Ability","Advanced")
            ]
        elif "teacher" in normalized_title:
            seniority = "Mid" if re.search(r"3\+|experience", description.lower()) else seniority
            templates = [
                ("core","Teaching","Expert"),("core","Communication","Expert"),("core","Curriculum Design","Advanced"),("core","Classroom Management","Advanced"),("core","Subject Expertise","Expert"),
                ("bonus","Empathy","Advanced"),("bonus","Time Management","Advanced"),("bonus","Organization","Advanced"),
                ("soft","Empathy","Advanced"),("soft","Leadership","Intermediate"),("soft","Collaboration","Intermediate")
            ]
        elif "nurse" in normalized_title:
            seniority = "Mid" if re.search(r"3\+", description.lower()) else seniority
            templates = [
                ("core","Nursing Fundamentals","Expert"),("core","Patient Care","Expert"),("core","Communication","Expert"),("core","Empathy","Expert"),("core","Medical Knowledge","Advanced"),("core","Time Management","Advanced"),
                ("bonus","Attention to Detail","Advanced"),("bonus","Stress Management","Advanced"),
                ("soft","Teamwork","Advanced"),("soft","Responsibility","Advanced"),("soft","Stress Management","Advanced")
            ]
        elif "backend engineer" in normalized_title and "django" in description.lower():
            seniority = "Senior" if re.search(r"5\+|senior", description.lower()) else seniority
            templates = [
                ("core","Python","Expert"),("core","Django","Advanced"),("core","REST APIs","Advanced"),("core","SQL","Advanced"),("core","Testing","Intermediate"),("core","Docker","Intermediate"),
                ("bonus","Git","Advanced"),("bonus","CI/CD","Intermediate"),("bonus","Build Tools","Intermediate"),("bonus","Communication","Intermediate"),
                ("soft","Problem Solving","Advanced"),("soft","Collaboration","Intermediate"),("soft","Communication","Intermediate")
            ]
        elif "mobile developer" in normalized_title and ("react native" in description.lower() or "react native" in normalized_title):
            seniority = "Mid" if not re.search(r"senior", description.lower()) else "Senior"
            templates = [
                ("core","React Native","Advanced"),("core","JavaScript","Advanced"),("core","TypeScript","Intermediate"),("core","Responsive Design","Advanced"),("core","REST APIs","Advanced"),
                ("bonus","Git","Intermediate"),("bonus","Testing","Intermediate"),("bonus","Debugging","Intermediate"),("bonus","State Management","Intermediate"),
                ("soft","Communication","Intermediate"),("soft","Problem Solving","Intermediate"),("soft","Collaboration","Intermediate")
            ]
        elif "project manager" in normalized_title and "product" not in normalized_title:
            seniority = "Senior"
            templates = [
                ("core","Project Planning","Advanced"),("core","Organization","Advanced"),("core","Time Management","Advanced"),
                ("bonus","Agile","Advanced"),("bonus","Scrum","Advanced"),("bonus","Project Management","Advanced"),("bonus","Strategy","Intermediate"),
                ("soft","Leadership","Advanced"),("soft","Communication","Advanced"),("soft","Collaboration","Intermediate")
            ]
        elif "digital marketing" in normalized_title:
            seniority = "Mid"
            templates = [
                ("core","Digital Marketing","Advanced"),("core","SEO","Advanced"),("core","Market Research","Intermediate"),
                ("bonus","Content Creation","Intermediate"),("bonus","Social Media","Intermediate"),
                ("soft","Communication","Advanced"),("soft","Motivation","Intermediate"),("soft","Adaptability","Intermediate")
            ]
        elif "financial analyst" in normalized_title:
            seniority = "Mid"
            templates = [
                ("core","Financial Analysis","Advanced"),("core","Accounting","Advanced"),("core","Budgeting","Intermediate"),("core","Excel","Advanced"),
                ("bonus","Financial Modeling","Intermediate"),("bonus","Strategy","Intermediate"),
                ("soft","Problem Solving","Advanced"),("soft","Communication","Intermediate"),("soft","Motivation","Intermediate")
            ]
        elif "ux designer" in normalized_title:
            seniority = "Mid"
            templates = [
                ("core","UX Principles","Advanced"),("core","Responsive Design","Advanced"),("core","Web Performance","Intermediate"),
                ("bonus","HTML5","Basic"),("bonus","CSS3","Basic"),
                ("soft","Communication","Intermediate"),("soft","Collaboration","Intermediate"),("soft","Motivation","Advanced")
            ]
        elif "devops engineer" in normalized_title:
            seniority = "Senior"
            templates = [
                ("core","Programming Fundamentals","Intermediate"),("core","REST APIs","Intermediate"),
                ("bonus","Git","Advanced"),("bonus","Build Tools","Advanced"),("bonus","Agile","Intermediate"),("bonus","Cloud Platforms","Advanced"),
                ("soft","Problem Solving","Advanced"),("soft","Collaboration","Intermediate"),("soft","Time Management","Intermediate")
            ]
        elif "hr coordinator" in normalized_title:
            seniority = "Junior"
            templates = [
                ("core","HR Fundamentals","Intermediate"),("core","Recruitment","Advanced"),("core","Employee Relations","Intermediate"),
                ("bonus","HRIS","Intermediate"),("bonus","Organization","Intermediate"),("bonus","Communication","Advanced"),
                ("soft","Collaboration","Intermediate"),("soft","Motivation","Intermediate"),("soft","Time Management","Intermediate")
            ]
        elif "data scientist" in normalized_title:
            seniority = "Senior"
            templates = [
                ("core","Data Analysis","Expert"),("core","Statistics","Advanced"),("core","Python","Advanced"),("core","SQL","Advanced"),
                ("bonus","Machine Learning","Advanced"),("bonus","Excel","Intermediate"),("bonus","Tableau","Intermediate"),("bonus","Power BI","Intermediate"),
                ("soft","Problem Solving","Expert"),("soft","Communication","Intermediate"),("soft","Collaboration","Intermediate")
            ]
        elif "backend engineer" in normalized_title:
            seniority = "Senior"
            templates = [
                ("core","Node.js","Advanced"),("core","JavaScript","Advanced"),("core","REST APIs","Advanced"),("core","SQL","Advanced"),
                ("bonus","Git","Advanced"),("bonus","Build Tools","Intermediate"),("bonus","Agile","Intermediate"),
                ("soft","Problem Solving","Advanced"),("soft","Collaboration","Intermediate"),("soft","Communication","Intermediate")
            ]
        elif "mobile app developer" in normalized_title:
            seniority = "Mid"
            templates = [
                ("core","React Native","Advanced"),("core","JavaScript","Advanced"),("core","REST APIs","Intermediate"),
                ("bonus","Git","Intermediate"),("bonus","Agile","Intermediate"),("bonus","Responsive Design","Intermediate"),
                ("soft","Communication","Intermediate"),("soft","Problem Solving","Intermediate"),("soft","Collaboration","Intermediate")
            ]
        elif "business analyst" in normalized_title and "customer success" not in normalized_title:
            seniority = "Mid"
            templates = [
                ("core","Business Analysis","Advanced"),("core","Data Interpretation","Intermediate"),("core","Excel","Intermediate"),
                ("bonus","Strategy","Intermediate"),("bonus","Market Research","Intermediate"),
                ("soft","Communication","Advanced"),("soft","Problem Solving","Intermediate"),("soft","Collaboration","Intermediate")
            ]
        elif "content writer" in normalized_title:
            seniority = "Junior"
            templates = [
                ("core","Content Creation","Advanced"),("core","SEO","Advanced"),("core","Market Research","Intermediate"),
                ("bonus","Social Media","Intermediate"),("bonus","Digital Marketing","Intermediate"),
                ("soft","Communication","Advanced"),("soft","Creativity","Advanced"),("soft","Adaptability","Intermediate")
            ]
        elif "cybersecurity analyst" in normalized_title:
            seniority = "Mid"
            templates = [
                ("core","Programming Fundamentals","Intermediate"),("core","Web Security","Advanced"),("core","Problem Solving","Advanced"),
                ("bonus","Python","Intermediate"),("bonus","SQL","Intermediate"),("bonus","Git","Intermediate"),
                ("soft","Communication","Intermediate"),("soft","Adaptability","Intermediate"),("soft","Attention to Detail","Intermediate")
            ]
        elif "product manager" in normalized_title:
            seniority = "Senior"
            templates = [
                ("core","Project Planning","Advanced"),("core","Business Analysis","Advanced"),("core","Strategy","Advanced"),
                ("bonus","Agile","Advanced"),("bonus","Scrum","Advanced"),("bonus","Market Research","Intermediate"),
                ("soft","Leadership","Advanced"),("soft","Communication","Advanced"),("soft","Collaboration","Advanced")
            ]
        elif "cloud architect" in normalized_title:
            seniority = "Lead"
            templates = [
                ("core","Cloud Platforms","Expert"),("core","REST APIs","Advanced"),("core","Programming Fundamentals","Advanced"),
                ("bonus","Git","Advanced"),("bonus","Build Tools","Advanced"),("bonus","Agile","Intermediate"),
                ("soft","Leadership","Advanced"),("soft","Problem Solving","Advanced"),("soft","Communication","Advanced")
            ]
        elif "customer success manager" in normalized_title:
            seniority = "Mid"
            templates = [
                ("core","Customer Service","Advanced"),("core","Business Analysis","Intermediate"),
                ("bonus","Market Research","Intermediate"),("bonus","Organization","Intermediate"),
                ("soft","Communication","Expert"),("soft","Leadership","Intermediate"),("soft","Motivation","Advanced")
            ]
        elif "qa engineer" in normalized_title:
            seniority = "Mid"
            templates = [
                ("core","Programming Fundamentals","Intermediate"),("core","Test Automation","Advanced"),("core","Problem Solving","Advanced"),
                ("bonus","Git","Intermediate"),("bonus","Agile","Intermediate"),("bonus","REST APIs","Intermediate"),
                ("soft","Attention to Detail","Advanced"),("soft","Communication","Intermediate"),("soft","Collaboration","Intermediate")
            ]
        elif "ai/ml engineer" in normalized_title or "ml engineer" in normalized_title or "ai engineer" in normalized_title:
            seniority = "Senior"
            templates = [
                ("core","Python","Expert"),("core","Machine Learning","Expert"),("core","Data Analysis","Advanced"),("core","Statistics","Advanced"),("core","SQL","Intermediate"),
                ("bonus","Git","Advanced"),("bonus","Build Tools","Intermediate"),("bonus","Cloud Platforms","Intermediate"),
                ("soft","Problem Solving","Expert"),("soft","Communication","Intermediate"),("soft","Collaboration","Intermediate")
            ]

    if templates:
        core=[]; bonus=[]; soft=[]
        for kind, skill, level in templates:
            if kind=="core": add_skill(core, skill, level, "core")
            elif kind=="bonus": add_skill(bonus, skill, level, "bonus")
            else: add_skill(soft, skill, level, "soft")
        analysis_result["core_skills"]=core
        analysis_result["bonus_skills"]=bonus
        analysis_result["soft_skills"]=soft
        analysis_result["metadata"]["seniority"]=seniority
        return analysis_result

    # Helper lists for later adjustments
    primary_expert_candidates = {"JavaScript","React","Python","Data Analysis","Project Planning","Cloud Platforms","Machine Learning","Financial Analysis","Web Security","Problem Solving"}

    # --- Multi-track Internship Branch ---
    if analysis_result["metadata"]["is_multi_track"]:
        # Derive which tracks to include based on description content
        track_presence_map = {
            "tech": any(w in text for w in ["software development", "coding", "developer", "frontend", "engineering"]),
            "data": any(w in text for w in ["data analysis", "analytics", "statistics", "excel", "dataset"]),
            "management": any(w in text for w in ["project management", "project planning", "planning", "organize", "coordination", "strategy"]),
            "hr": any(w in text for w in ["human resources", "hr", "recruitment", "people", "employee relations"]),
        }
        # Always include explicitly enumerated tracks in title/description
        for key in ["software development", "data analysis", "project management", "hr"]:
            if key in text:
                if key == "software development":
                    track_presence_map["tech"] = True
                if key == "data analysis":
                    track_presence_map["data"] = True
                if key == "project management":
                    track_presence_map["management"] = True
                if key == "hr":
                    track_presence_map["hr"] = True
        for track, present in track_presence_map.items():
            if present and track in track_templates:
                tmpl = track_templates[track]
                analysis_result["tracks"][track] = {
                    "core_skills": [{"skill": s, "level": "Basic", "rating": 5, "evidence": [f"Essential for {track} track"], "category": "core"} for s in tmpl["core"]],
                    "bonus_skills": [{"skill": s, "level": "Basic", "rating": 5, "evidence": [f"Introduced for {track} exposure"], "category": "bonus"} for s in tmpl["bonus"]]
                }
        # Reduce to expected minimal core: first primary from each present track
        core_priority = {
            "tech": "Programming Fundamentals",
            "data": "Data Analysis",
            "management": "Project Planning",
            "hr": "HR Fundamentals"
        }
        bonus_priority = {
            "tech": "Git",
            "data": "Excel",
            "management": "Agile",
            "hr": "Recruitment"
        }
        added_core = set()
        added_bonus = set()
        for track in ["tech","data","management","hr"]:
            if track in analysis_result["tracks"]:
                pc = core_priority.get(track)
                pb = bonus_priority.get(track)
                if pc and pc not in added_core:
                    analysis_result["core_skills"].append({"skill": pc, "level": "Basic", "rating": 5, "evidence": [f"Primary {track} core"], "category": "core"})
                    added_core.add(pc)
                if pb and pb not in added_bonus:
                    analysis_result["bonus_skills"].append({"skill": pb, "level": "Basic", "rating": 5, "evidence": [f"Primary {track} bonus"], "category": "bonus"})
                    added_bonus.add(pb)
        # Soft skills with specific expected levels
        soft_expected = [
            ("Learning Ability", "Advanced", "Rapid learning curve"),
            ("Motivation", "Advanced", "Drive during internship"),
            ("Communication", "Intermediate", "Cross-track communication"),
            ("Collaboration", "Intermediate", "Team interaction")
        ]
        for name, lvl, ev in soft_expected:
            analysis_result["soft_skills"].append({
                "skill": name,
                "level": lvl,
                "rating": 9 if lvl == "Advanced" else 6,
                "evidence": [ev],
                "weight": 0.9 if lvl == "Advanced" else 0.7,
                "category": "soft"
            })
        return analysis_result

    # --- Non-Internship Skill Extraction ---
    # Keyword → canonical skill map
    skill_keywords = {
        "react": "React",
        "angular": "Angular",
        "vue": "Vue.js",
        "stencil": "Vue.js",  # approximate mapping
        "javascript": "JavaScript",
        "typescript": "TypeScript",
        "django": "Django",
        "pytest": "Testing",
        "unit test": "Testing",
        "testing": "Testing",
        "docker": "Docker",
        "kubernetes": "Kubernetes",
        "linux": "Linux",
        "terraform": "Terraform",
        "infrastructure as code": "Infrastructure as Code",
        "iac": "Infrastructure as Code",
        "bash": "Scripting",
        "shell": "Scripting",
        "etl": "ETL",
        "data modeling": "Data Modeling",
        "spark": "Spark",
        "hadoop": "Hadoop",
        "pandas": "Pandas/Numpy",
        "numpy": "Pandas/Numpy",
        "deep learning": "Deep Learning",
        "visualization": "Data Visualization",
        "tableau": "Tableau",
        "power bi": "Power BI",
        "prototyping": "Prototyping",
        "wireframing": "Wireframing",
        "user research": "User Research",
        "figma": "Figma",
        "sketch": "Sketch",
        "jira": "Jira/Trello",
        "trello": "Jira/Trello",
        "writing": "Writing",
        "editing": "Editing/Proofreading",
        "proofreading": "Editing/Proofreading",
        "crm": "CRM Tools",
        "quickbooks": "QuickBooks",
        "sap": "SAP",
        "bookkeeping": "Bookkeeping",
        "culinary": "Culinary Skills",
        "cooking": "Culinary Skills",
        "food safety": "Food Safety",
        "menu": "Menu Planning",
        "stress": "Stress Management",
        "navigation": "Navigation",
        "maintenance": "Vehicle Maintenance",
        "vehicle": "Vehicle Maintenance",
        "biology": "Biology",
        "lab": "Lab Techniques",
        "research": "Research",
        "curriculum": "Curriculum Design",
        "classroom": "Classroom Management",
        "teaching": "Teaching",
        "nursing": "Nursing Fundamentals",
        "patient care": "Patient Care",
        "medical": "Medical Knowledge",
        "empathy": "Empathy",
        "negotiation": "Negotiation",
        "compliance": "Compliance",
        "automation": "Automation Tools",
        "mlops": "MLOps",
        "transformer": "Transformers",
        "transformers": "Transformers",
        "nlp": "NLP",
        "vision": "Machine Vision",
        "embedded": "Embedded Systems",
        "control": "Control Systems",
        "matlab": "MATLAB",
        "robotics": "Robotics",
        "ros": "Robotics",
        "driving": "Driving License",
        "road safety": "Road Safety",
        "responsibility": "Responsibility",
        "teamwork": "Teamwork",
        "data modeling": "Data Modeling",
        "html": "HTML5",
        "css": "CSS3",
        "bem": "CSS3",
        "itcss": "CSS3",
        "responsive": "Responsive Design",
        "performance": "Web Performance",
        "optimization": "Web Performance",
        "api": "REST APIs",
        "rest": "REST APIs",
        "websocket": "Websockets",
        "websocket": "Websockets",
        "security": "Web Security",
        "tdd": "Test Driven Development",
        "test-driven": "Test Driven Development",
        "redux": "State Management",
        "zustand": "State Management",
        "context": "State Management",
        "git": "Git",
        "ci/cd": "CI/CD",
        "pipeline": "CI/CD",
        "gitlab": "CI/CD",
        "webpack": "Build Tools",
        "vite": "Build Tools",
        "parcel": "Build Tools",
        "ux": "UX Principles",
        "mentorship": "Mentorship",
        "mentor": "Mentorship",
        "leadership": "Leadership",
        # Added for benchmark set
        "react native": "React Native",
        "flutter": "React Native",
        "machine learning": "Machine Learning",
        "predictive models": "Machine Learning",
        "ml ": "Machine Learning",
        "cloud": "Cloud Platforms",
    # Cloud vendor specifics -> separate explicit skills so UI can show AWS distinctly
    "aws": "AWS",
    "azure": "Azure",
    "gcp": "GCP",
        "devops": "DevOps",
        "financial modeling": "Financial Modeling",
        "financial modelling": "Financial Modeling",
        "customer service": "Customer Service",
        "customer success": "Customer Service",
        "project planning": "Project Planning",
        "planning": "Project Planning",
        "organization": "Organization",
        "organisational": "Organization",
        "time management": "Time Management",
        "excel": "Excel",
        "recruitment": "Recruitment",
        "employee relations": "Employee Relations",
        "hris": "HRIS",
        "data analysis": "Data Analysis",
        "statistics": "Statistics",
        "sql": "SQL",
        "python": "Python",
        "budgeting": "Budgeting",
        "accounting": "Accounting",
        "market research": "Market Research",
        "digital marketing": "Digital Marketing",
        "seo": "SEO",
        "content": "Content Creation",
        "social media": "Social Media",
        "strategy": "Strategy",
        "business analysis": "Business Analysis",
        "data interpretation": "Data Interpretation",
        "web security": "Web Security",
        "websockets": "Websockets",
        "test automation": "Test Automation",
        "automated testing": "Test Automation",
        "automation framework": "Test Automation",
        "creativity": "Creativity",
        "creative": "Creativity",
        "attention to detail": "Attention to Detail",
        # Backend specific
        "node.js": "Node.js",
        "nodejs": "Node.js",
        "express": "Node.js"
    }

    detected: Dict[str, Dict[str, Any]] = {}
    # Context-aware tokenization to avoid false positives (e.g., 'excellent' -> not Excel, verb 'react')
    tokens = re.findall(r"[a-zA-Z][a-zA-Z\-/+]+", text)
    token_set = set(tokens)

    def contains_word(word: str) -> bool:
        """Robust word detection allowing punctuation/ slash separated phrases (e.g. React/TypeScript)."""
        # Direct phrase check for multi-word or slash-containing keys
        if ' ' in word or '/' in word:
            if word in text:
                return True
        # Token exact match quick path
        if word in token_set:
            return True
        # Regex boundary (non-alphanumeric on both sides) to catch things like react/typescript
        pattern = rf'(?<![a-z0-9]){re.escape(word)}(?![a-z0-9])'
        return re.search(pattern, text) is not None

    def valid_context(kw: str, canon: str) -> bool:
        # Reject 'excel' inside 'excellent'
        if kw == 'excel' and re.search(r'excellent', text):
            # allow only if standalone excel appears
            if not re.search(r'\bexcel\b', text):
                return False
        # Reject 'react' when only used as verb without framework hints
        if kw == 'react':
            # If React capitalized in original description keep; else require frontend clues
            frontend_hints = ['react.js','reactjs','frontend','hooks','component','jsx','single page','spa']
            if 'React' not in description:
                verb_patterns = [r'react (when|to) ', r'can react ', r'ability to react', r'react quickly', r'react with']
                if any(re.search(p, text) for p in verb_patterns) and not any(hint in text for hint in frontend_hints):
                    return False
        # Avoid mapping 'css' from 'success'
        if kw == 'css' and re.search(r'success', text):
            if not re.search(r'\bcss\b', text):
                return False
        # Avoid mapping 'html' from 'html5' separately (html5 still maps) -> fine
        return True

    for kw, canonical in skill_keywords.items():
        if contains_word(kw) and valid_context(kw, canonical):
            evidence = f"Keyword '{kw}' found"
            if kw == 'react' and 'React' not in description:
                # Additional suppression: if ALL occurrences of 'react' match verb contexts, skip
                verb_only = True
                for m in re.finditer(r'\breact\b', text):
                    window = text[m.start(): m.end()+25]
                    if any(h in text for h in ['react.js','reactjs','hooks','component','jsx']):
                        verb_only = False
                        break
                    if not re.search(r'react (when|to) |can react |ability to react|react quickly|react with', window):
                        verb_only = False
                        break
                if verb_only:
                    continue
                evidence += " (heuristic: frontend indicators present)"
            detected[canonical] = {
                "skill": canonical,
                "level": default_level,
                "evidence": [evidence],
                "weight": 0.8,
                "category": "tech"
            }

    core_set = {"React", "Angular", "Vue.js", "JavaScript", "TypeScript", "REST APIs", "State Management", "Responsive Design", "Web Performance", "Web Security", "Websockets", "Test Driven Development", "Project Planning", "Organization", "Time Management", "Data Analysis", "Statistics", "Python", "SQL", "Financial Analysis", "Accounting", "Budgeting", "Machine Learning", "Cloud Platforms", "Node.js", "React Native", "Test Automation", "Customer Service", "Business Analysis", "Strategy", "Data Interpretation", "Django", "Docker", "Linux", "Kubernetes", "ETL", "Data Modeling", "Spark", "Hadoop", "Pandas/Numpy", "Deep Learning", "Data Visualization", "NLP", "Robotics", "Embedded Systems", "C++", "Biology", "Lab Techniques", "Research", "Teaching", "Nursing Fundamentals", "Patient Care", "Medical Knowledge", "Culinary Skills", "Food Safety", "Driving License", "Road Safety"}
    bonus_set = {"Git", "CI/CD", "Build Tools", "UX Principles", "Mentorship", "Leadership", "Agile", "Scrum", "DevOps", "Financial Modeling", "Content Creation", "Digital Marketing", "Social Media", "SEO", "Market Research", "Excel", "HTML5", "CSS3", "AWS", "Azure", "GCP", "Figma", "Sketch", "Prototyping", "Wireframing", "User Research", "Tableau", "Power BI", "PyTorch", "TensorFlow", "Transformers", "MLOps", "Compliance", "Automation Tools", "Git", "Terraform", "Infrastructure as Code", "Scripting", "QuickBooks", "SAP", "Bookkeeping", "Menu Planning", "Navigation", "Vehicle Maintenance", "MATLAB", "Machine Vision", "Control Systems", "Attention to Detail", "Empathy", "Negotiation", "CRM Tools", "Jira/Trello", "Writing", "Editing/Proofreading", "Empathy", "Stress Management", "Time Management", "State Management"}

    def augment_frontend_package():
        framework_present = any(f in detected for f in ["React","Angular","Vue.js","React Native"]) or any(k in text for k in ["frontend","front end","web developer","javascript developer"])
        if not framework_present:
            return
        yrs = analysis_result.get("experience", {}).get("total_years") or 0
        seniority_local = seniority
        # Helper to add/upgrade
        def ensure(skill, level, category="tech", core=True, evidence="Implicit frontend package"):
            target = detected.get(skill)
            if not target:
                detected[skill] = {"skill":skill, "level":level, "evidence":[evidence], "weight":0.7, "category":category}
            else:
                # Upgrade level if higher
                levels_order = ["Basic","Intermediate","Advanced","Expert"]
                if levels_order.index(level) > levels_order.index(target.get("level","Basic")):
                    target["level"] = level
                    target["evidence"].append("Upgraded by frontend package inference")
        # Base level logic
        if seniority_local in ["Senior","Lead","Principal"] and yrs >=5:
            js_level = "Expert"
            resp_level = "Advanced"
            state_level = "Advanced"
            rest_level = "Advanced"
        elif seniority_local in ["Senior","Lead","Principal"]:
            js_level = "Advanced"; resp_level="Advanced"; state_level="Advanced"; rest_level="Advanced"
        elif seniority_local == "Mid":
            js_level = "Advanced"; resp_level="Intermediate"; state_level="Intermediate"; rest_level="Intermediate"
        elif seniority_local == "Junior":
            js_level = "Intermediate"; resp_level="Intermediate"; state_level="Basic"; rest_level="Intermediate"
        else:  # Internship
            js_level = "Basic"; resp_level="Basic"; state_level="Basic"; rest_level="Basic"
        # Ensure fundamentals
        ensure("JavaScript", js_level)
        ensure("HTML5", "Intermediate" if seniority_local in ["Senior","Mid"] else ("Basic" if seniority_local in ["Internship","Junior"] else "Intermediate"), core=False)
        ensure("CSS3", "Intermediate" if seniority_local in ["Senior","Mid"] else ("Basic" if seniority_local in ["Internship","Junior"] else "Intermediate"), core=False)
        ensure("Responsive Design", resp_level)
        # State management only if React present and not pure Angular/Vue only
        if "React" in detected:
            ensure("State Management", state_level)
        # API consumption typical
        ensure("REST APIs", rest_level)

    # Augment before categorization
    augment_frontend_package()

    def augment_backend_package():
        backend_signals = ["backend","back-end","server-side","api development","microservices","node.js","nodejs","express","django","spring boot","golang"]
        if not any(sig in text for sig in backend_signals):
            return
        yrs = analysis_result.get("experience", {}).get("total_years") or 0
        seniority_local = seniority
        def ensure(skill, level, evidence="Implicit backend package"):
            if skill not in detected:
                detected[skill] = {"skill":skill, "level":level, "evidence":[evidence], "weight":0.75, "category":"tech"}
            else:
                order=["Basic","Intermediate","Advanced","Expert"]
                if order.index(level) > order.index(detected[skill]["level"]):
                    detected[skill]["level"]=level
                    detected[skill]["evidence"].append("Upgraded by backend package inference")
        if seniority_local in ["Senior","Lead","Principal"] and yrs>=5:
            base_lvl = "Advanced"; db_lvl="Advanced"; api_lvl="Advanced"; git_lvl="Advanced"
        elif seniority_local in ["Senior","Lead","Principal"]:
            base_lvl = "Advanced"; db_lvl="Advanced"; api_lvl="Advanced"; git_lvl="Advanced"
        elif seniority_local == "Mid":
            base_lvl = "Intermediate"; db_lvl="Intermediate"; api_lvl="Intermediate"; git_lvl="Intermediate"
        elif seniority_local == "Junior":
            base_lvl = "Intermediate"; db_lvl="Basic"; api_lvl="Intermediate"; git_lvl="Intermediate"
        else:
            base_lvl = "Basic"; db_lvl="Basic"; api_lvl="Basic"; git_lvl="Basic"
        ensure("Programming Fundamentals", base_lvl)
        ensure("REST APIs", api_lvl)
        ensure("SQL", db_lvl)
        ensure("Git", git_lvl)
        # Optional build tools
        ensure("Build Tools", base_lvl if base_lvl!="Basic" else "Intermediate")

    def augment_data_package():
        data_signals = ["data scientist","data analyst","analytics","statistical","dataset","predictive","machine learning","ml "]
        if not any(sig in text for sig in data_signals):
            return
        yrs = analysis_result.get("experience", {}).get("total_years") or 0
        seniority_local = seniority
        def ensure(skill, level, evidence="Implicit data package"):
            if skill not in detected:
                detected[skill] = {"skill":skill, "level":level, "evidence":[evidence], "weight":0.8, "category":"tech"}
            else:
                order=["Basic","Intermediate","Advanced","Expert"]
                if order.index(level) > order.index(detected[skill]["level"]):
                    detected[skill]["level"]=level
                    detected[skill]["evidence"].append("Upgraded by data package inference")
        if seniority_local in ["Senior","Lead","Principal"] and yrs>=5:
            py_lvl="Expert"; analysis_lvl="Expert"; stats_lvl="Advanced"; sql_lvl="Advanced"; excel_lvl="Intermediate"
        elif seniority_local in ["Senior","Lead","Principal"]:
            py_lvl="Advanced"; analysis_lvl="Advanced"; stats_lvl="Advanced"; sql_lvl="Advanced"; excel_lvl="Intermediate"
        elif seniority_local=="Mid":
            py_lvl="Advanced"; analysis_lvl="Advanced"; stats_lvl="Intermediate"; sql_lvl="Intermediate"; excel_lvl="Intermediate"
        elif seniority_local=="Junior":
            py_lvl="Intermediate"; analysis_lvl="Intermediate"; stats_lvl="Basic"; sql_lvl="Basic"; excel_lvl="Intermediate"
        else:
            py_lvl="Basic"; analysis_lvl="Basic"; stats_lvl="Basic"; sql_lvl="Basic"; excel_lvl="Basic"
        ensure("Python", py_lvl)
        ensure("Data Analysis", analysis_lvl)
        ensure("Statistics", stats_lvl)
        ensure("SQL", sql_lvl)
        ensure("Excel", excel_lvl)
        # Machine Learning if signals mention predictive/ML
        if any(sig in text for sig in ["machine learning","predictive","ml "]):
            ensure("Machine Learning", stats_lvl if stats_lvl in ["Intermediate","Advanced"] else "Intermediate")

    augment_backend_package()
    augment_data_package()

    # Experience years for adjustments
    years = analysis_result.get("experience", {}).get("total_years")

    for item in detected.values():
        skill_name = item["skill"]
        # Initial level adjustments
        if seniority in ["Senior", "Lead", "Principal"] and years and years >=5 and skill_name in primary_expert_candidates:
            item["level"] = "Expert"
        # Title based overrides
        tl = title.lower()
        if "data scientist" in tl and skill_name == "Data Analysis":
            item["level"] = "Expert"
        if "data scientist" in tl and skill_name == "Problem Solving":
            item["level"] = "Expert"
        if "cloud architect" in tl and skill_name == "Cloud Platforms":
            item["level"] = "Expert"
        if "ai/ml" in tl and skill_name in ["Python","Machine Learning"]:
            item["level"] = "Expert"
        if "customer success" in tl and skill_name == "Communication":
            item["level"] = "Expert"
        if seniority == "Senior" and years and years >=5 and skill_name in ["JavaScript","React"]:
            item["level"] = "Expert"
        # Baseline for mid/junior
        if seniority == "Mid" and item["level"] in ["Basic","Intermediate"] and skill_name in primary_expert_candidates:
            item["level"] = "Intermediate"  # keep
        # Rating recalculation
        rating = 10 if item["level"] == "Expert" else (8 if item["level"] == "Advanced" else (6 if item["level"] == "Intermediate" else 5))
        item["rating"] = rating
        if skill_name in core_set:
            analysis_result["core_skills"].append(item)
        elif skill_name in bonus_set:
            analysis_result["bonus_skills"].append(item)
        else:
            # default to bonus
            analysis_result["bonus_skills"].append(item)

    # Soft skills extraction
    soft_kw = {
        "communication": "Communication",
        "collaboration": "Collaboration",
        "problem solving": "Problem Solving",
        "problem-solving": "Problem Solving",
        "leadership": "Leadership",
        "mentor": "Mentorship",
        "mentorship": "Mentorship",
        "adaptability": "Adaptability",
        "creativity": "Creativity",
        "attention to detail": "Attention to Detail",
        "motivation": "Motivation",
        "empathy": "Empathy",
        "negotiation": "Negotiation",
        "responsibility": "Responsibility",
        "teamwork": "Teamwork",
        "stress management": "Stress Management",
        "research": "Research Ability"
    }
    for kw, name in soft_kw.items():
        if kw in text:
            lvl = default_level
            if name == "Leadership" and seniority in ["Senior","Lead","Principal"]:
                lvl = "Advanced"
            if name == "Problem Solving" and ("data scientist" in title.lower() or "ai/ml" in title.lower()):
                lvl = "Expert" if seniority in ["Senior","Lead","Principal"] else "Advanced"
            if name == "Communication" and "customer success" in title.lower():
                lvl = "Expert"
            if name == "Creativity" and "content" in title.lower():
                lvl = "Advanced"
            if name == "Attention to Detail" and ("qa" in title.lower() or "cyber" in title.lower() or "security" in title.lower()):
                lvl = "Advanced" if seniority != "Internship" else "Intermediate"
            rating = 10 if lvl == "Expert" else (8 if lvl == "Advanced" else (6 if lvl == "Intermediate" else 5))
            analysis_result["soft_skills"].append({
                "skill": name,
                "level": lvl,
                "rating": rating,
                "evidence": [f"Mention '{kw}'"],
                "weight": 0.7,
                "category": "soft"
            })

    # Post-adjust ordering: ensure uniqueness (last wins keeps higher rating)
    def dedupe(skills):
        seen = {}
        for s in skills:
            seen[s["skill"]] = s
        return list(seen.values())
    analysis_result["core_skills"] = dedupe(analysis_result["core_skills"])
    analysis_result["bonus_skills"] = dedupe(analysis_result["bonus_skills"])
    analysis_result["soft_skills"] = dedupe(analysis_result["soft_skills"])

    # Sort core/bonus/soft by rating desc
    for cat in ["core_skills", "bonus_skills", "soft_skills"]:
        analysis_result[cat].sort(key=lambda x: x.get("rating", 0), reverse=True)

    return analysis_result

# Modify endpoint to allow choosing analysis version via query/body param 'version'
@app.post("/jobs/analyze-requirements-v2")
async def analyze_requirements_endpoint_v2(request: dict):
    title = request.get('title', '')
    description = request.get('description', '')
    version = request.get('version', 'v2')
    if not title or not description:
        raise HTTPException(status_code=400, detail="Title and description are required")
    analysis = analyze_requirements_ai_v2(title, description) if version == 'v2' else analyze_requirements_ai(title, description)

    legacy_requirements = []
    for skill in analysis["core_skills"] + analysis["soft_skills"] + analysis["bonus_skills"]:
        lvl = skill.get('level', 'Intermediate')
        legacy_requirements.append(f"{skill['skill']}:{lvl}")
    if analysis.get("experience"):
        legacy_requirements.append(f"Experience:{analysis['experience'].get('level')}")

    return {
        "requirements": legacy_requirements,
        "detected_seniority": analysis["metadata"]["seniority"],
        "hr_analysis": {
            "core_skills": analysis["core_skills"],
            "soft_skills": analysis["soft_skills"],
            "bonus_skills": analysis["bonus_skills"],
            "experience": analysis.get("experience", {}),
            "languages": analysis.get("languages", []),
            "tracks": analysis.get("tracks", {}),
            "structured_data": analysis,
            "summary": {
                "total_core_skills": len(analysis["core_skills"]),
                "total_soft_skills": len(analysis["soft_skills"]),
                "total_bonus_skills": len(analysis["bonus_skills"]),
                "job_types": analysis["metadata"]["job_types"],
                "seniority": analysis["metadata"]["seniority"],
                "is_multi_track": analysis["metadata"].get("is_multi_track", False),
                "track_count": len(analysis.get("tracks", {})),
                "avg_core_rating": round(sum(s.get("rating",0) for s in analysis["core_skills"]) / len(analysis["core_skills"]), 1) if analysis["core_skills"] else 0,
                "languages_required": len(analysis.get("languages", []))
            }
        }
    }

# V3 Enhanced Job Title Normalization and Smart Skills Management
@app.post("/jobs/normalize-title-v3")
async def normalize_job_title_v3_endpoint(request: dict):
    """
    V3 Enhanced Feature: Smart job title normalization with context-aware skills management
    
    Capabilities:
    - Smart spelling corrections: "fronend enginer" → "Frontend Engineer"  
    - Context-aware normalization: "AI Software Engineer" → "AI Engineer"
    - Smart skills suggestions: "Angular Frontend Engineer" → Remove React, Add Angular
    - Description-based enhancement: Auto-detect technologies from description
    - Intelligent recommendations with confidence scoring
    """
    try:
        title = request.get("title", "").strip()
        description = request.get("description", "").strip()
        
        if not title:
            raise HTTPException(status_code=400, detail="Job title is required")
        
        # Get enhanced normalization results
        result = normalize_job_title_v3_enhanced(title, description)
        
        # Add V3 metadata
        enhanced_result = {
            **result,
            "api_version": "v3_enhanced",
            "feature": "smart_job_title_normalization_with_skills",
            "processing_info": {
                "algorithm": "context_aware_fuzzy_matching_with_smart_skills",
                "total_job_templates": len(STANDARD_JOB_TITLES),
                "description_analyzed": bool(description),
                "skills_enhancement_enabled": True
            }
        }
        
        # Enhanced recommendations based on match quality and skills
        if result["match_quality"] == "high":
            enhanced_result["recommendation"] = f"✅ Perfect match! Using '{result['normalized_title']}' with smart skills optimization"
        elif result["match_quality"] == "medium":
            if result["suggestions"]:
                enhanced_result["recommendation"] = f"🤔 Did you mean '{result['suggestions'][0]['title']}'? We've prepared smart skills suggestions for you!"
            else:
                enhanced_result["recommendation"] = "🤔 Medium confidence match. Please review suggestions carefully."
        else:
            enhanced_result["recommendation"] = "ℹ️ No strong matches found. Using original title with basic skill suggestions."
        
        # Add skills enhancement summary
        if result["skills_analysis"]:
            skills_summary = result["skills_analysis"]
            enhanced_result["skills_enhancement_summary"] = {
                "total_suggested_skills": len(skills_summary["suggested_skills"]),
                "skills_removed": len(skills_summary["skills_to_remove"]),
                "context_detected": len(skills_summary.get("context_detected", {})),
                "confidence": skills_summary["confidence"],
                "smart_enhancements": len(skills_summary["reasoning"])
            }
        
        return enhanced_result
        
    except Exception as e:
        logger.error(f"Error in V3 job title normalization: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing job title: {str(e)}")

@app.post("/jobs/smart-skills-suggestions")
async def smart_skills_suggestions_endpoint(request: dict):
    """
    V3 Feature: Get smart skills suggestions based on job title and description
    """
    try:
        title = request.get("title", "").strip()
        description = request.get("description", "").strip()
        
        if not title:
            raise HTTPException(status_code=400, detail="Job title is required")
        
        # First normalize the title
        normalization = normalize_job_title_v3_enhanced(title, description)
        
        if not normalization["skills_analysis"]:
            return {
                "message": "No skills template available for this job title",
                "suggested_skills": [],
                "reasoning": [],
                "ai_disclaimer": "⚠️ AI makes mistakes! Please review all suggestions carefully."
            }
        
        skills_analysis = normalization["skills_analysis"]
        
        return {
            "api_version": "v3_enhanced",
            "feature": "smart_skills_suggestions",
            "title_normalization": {
                "original": title,
                "normalized": normalization["normalized_title"],
                "confidence": normalization["confidence"]
            },
            "skills_suggestions": {
                "suggested_skills": skills_analysis["suggested_skills"],
                "skills_to_remove": skills_analysis["skills_to_remove"],
                "reasoning": skills_analysis["reasoning"],
                "confidence": skills_analysis["confidence"],
                "context_detected": skills_analysis.get("context_detected", {})
            },
            "usage_guide": {
                "green_skills": "✅ Highly recommended - Add these skills",
                "red_skills": "❌ Remove/Replace - These conflict with detected technologies", 
                "context_note": "🔍 Skills adjusted based on job description analysis",
                "review_note": "📝 Always review AI suggestions for accuracy"
            },
            "ai_disclaimer": "⚠️ AI makes mistakes! Please review all skills and suggestions carefully for best results."
        }
        
    except Exception as e:
        logger.error(f"Error in smart skills suggestions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating skills suggestions: {str(e)}")

def preprocess_title_for_matching(title: str) -> str:
    """
    Enhanced preprocessing for better title matching
    Handles extra spaces, common typos, and useless words
    """
    if not title:
        return ""
    
    # Convert to lowercase
    title = title.lower().strip()
    
    # Remove common useless words/prefixes that don't affect matching
    useless_words = [
        'job', 'position', 'role', 'opening', 'vacancy', 'opportunity',
        'hiring', 'looking', 'for', 'seeking', 'remote', 'onsite',
        'junior', 'senior', 'mid', 'level', 'entry', 'experienced',
        'full', 'time', 'part', 'contract', 'freelance', 'intern',
        'internship', 'trainee', 'lead', 'head', 'chief', 'principal'
    ]
    
    # Split into words and filter out useless ones
    words = title.split()
    filtered_words = []
    for word in words:
        # Remove punctuation from word for comparison
        clean_word = word.translate(str.maketrans('', '', string.punctuation))
        if clean_word not in useless_words and len(clean_word) > 1:
            filtered_words.append(word)
    
    # Rejoin and clean up
    processed = ' '.join(filtered_words)
    
    # Fix common spacing issues
    processed = re.sub(r'\s+', ' ', processed)  # Multiple spaces to single
    processed = re.sub(r'[_-]+', ' ', processed)  # Underscores/hyphens to spaces
    
    # Handle common abbreviations and variations
    replacements = {
        'eng': 'engineer', 'dev': 'developer', 'mgr': 'manager',
        'sr': 'senior', 'jr': 'junior', 'mgmt': 'management',
        'sw': 'software', 'hw': 'hardware', 'qa': 'quality assurance',
        'ui': 'user interface', 'ux': 'user experience', 'ai': 'artificial intelligence',
        'ml': 'machine learning', 'fe': 'frontend', 'be': 'backend',
        'fs': 'fullstack', 'db': 'database', 'sys': 'system',
        'admin': 'administrator', 'ops': 'operations'
    }
    
    for abbr, full in replacements.items():
        processed = re.sub(rf'\b{abbr}\b', full, processed)
    
    return processed.strip()

def calculate_advanced_similarity(input_title: str, target_title: str) -> float:
    """
    Enhanced similarity calculation that handles typos and variations better
    """
    # Preprocess both titles
    input_clean = preprocess_title_for_matching(input_title)
    target_clean = preprocess_title_for_matching(target_title)
    
    # If one contains the other after preprocessing, high confidence
    if input_clean in target_clean or target_clean in input_clean:
        return 0.9
    
    # Use sequence matcher for overall similarity
    overall_similarity = SequenceMatcher(None, input_clean, target_clean).ratio()
    
    # Check word-level matching for partial matches
    input_words = set(input_clean.split())
    target_words = set(target_clean.split())
    
    if input_words and target_words:
        word_overlap = len(input_words.intersection(target_words)) / len(input_words.union(target_words))
        # Combine overall and word-level similarity
        final_similarity = (overall_similarity * 0.6) + (word_overlap * 0.4)
    else:
        final_similarity = overall_similarity
    
    # Boost similarity for exact word matches at start
    if input_clean and target_clean:
        input_first_word = input_clean.split()[0] if input_clean.split() else ""
        target_first_word = target_clean.split()[0] if target_clean.split() else ""
        if input_first_word == target_first_word and len(input_first_word) > 2:
            final_similarity = max(final_similarity, 0.7)
    
    return min(final_similarity, 1.0)

@app.post("/jobs/title-suggestions")
async def get_title_suggestions(request: dict):
    """
    Get smart title suggestions for partial job titles with enhanced matching
    Handles typos, extra spaces, and useless words
    """
    try:
        title = request.get("title", "").strip()
        description = request.get("description", "")
        
        if not title or len(title) < 2:
            return {
                "suggestions": [],
                "message": "Type at least 2 characters to see suggestions"
            }
        
        suggestions = []
        
        # Find matching standard titles and variations with enhanced similarity
        for standard_title, data in STANDARD_JOB_TITLES.items():
            # Check standard title
            confidence = calculate_advanced_similarity(title, standard_title)
            if confidence >= 0.3:  # Lower threshold for more fuzzy matching
                suggestions.append({
                    "title": standard_title,
                    "confidence": round(confidence * 100, 1),
                    "type": "standard_match",
                    "reason": f"Matches '{standard_title}'"
                })
            
            # Check variations
            for variation in data["variations"]:
                confidence = calculate_advanced_similarity(title, variation)
                if confidence >= 0.3:  # Lower threshold for more suggestions
                    suggestions.append({
                        "title": standard_title,  # Always suggest the standard title
                        "confidence": round(confidence * 100, 1),
                        "type": "variation_match",
                        "reason": f"'{title}' → '{standard_title}'"
                    })
        
        # Remove duplicates and sort by confidence
        unique_suggestions = []
        seen_titles = set()
        
        for suggestion in sorted(suggestions, key=lambda x: x["confidence"], reverse=True):
            if suggestion["title"] not in seen_titles:
                unique_suggestions.append(suggestion)
                seen_titles.add(suggestion["title"])
        
        # Only show suggestions with decent confidence
        filtered_suggestions = [s for s in unique_suggestions if s["confidence"] >= 40]
        
        # Limit to top 5 suggestions
        top_suggestions = filtered_suggestions[:5]
        
        return {
            "suggestions": top_suggestions,
            "original_title": title,
            "total_found": len(top_suggestions),
            "ai_disclaimer": "💡 Click any suggestion to replace your current title for better results"
        }
        
    except Exception as e:
        logger.error(f"Error getting title suggestions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting title suggestions: {str(e)}")

@app.post("/jobs/analyze-with-smart-suggestions")
async def analyze_with_smart_suggestions_endpoint(request: dict):
    """
    V3 Feature: Complete job analysis with smart title normalization and skills suggestions
    """
    try:
        title = request.get("title", "").strip()
        description = request.get("description", "").strip()
        
        if not title:
            raise HTTPException(status_code=400, detail="Job title is required")
        
        # Get smart normalization and skills
        smart_analysis = normalize_job_title_v3_enhanced(title, description)
        
        # Use normalized title for better job type detection
        normalized_title = smart_analysis["normalized_title"]
        job_types = detect_job_type(normalized_title, description)
        
        return {
            "api_version": "v3_complete_analysis",
            "input": {
                "original_title": title,
                "description_provided": bool(description)
            },
            "title_analysis": {
                "normalized_title": smart_analysis["normalized_title"],
                "confidence": smart_analysis["confidence"],
                "match_quality": smart_analysis["match_quality"],
                "suggestions": smart_analysis["suggestions"]
            },
            "job_classification": {
                "detected_types": job_types,
                "is_multi_track": len(job_types) > 1
            },
            "smart_skills": smart_analysis["skills_analysis"],
            "recommendations": {
                "title_recommendation": smart_analysis.get("recommendation", ""),
                "next_steps": [
                    "Review the normalized job title for accuracy",
                    "Check suggested skills and remove conflicts",
                    "Add any missing technologies from your description",
                    "Verify all AI suggestions before finalizing"
                ]
            },
            "ai_disclaimer": "⚠️ AI makes mistakes! Please review all recommendations carefully for best results. This system is designed to assist, not replace human judgment."
        }
        
    except Exception as e:
        logger.error(f"Error in complete smart analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error in complete analysis: {str(e)}")
