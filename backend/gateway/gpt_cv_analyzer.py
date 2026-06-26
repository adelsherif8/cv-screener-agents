# GPT-Powered CV Analysis System
# This module implements CV analysis using OpenAI GPT instead of hardcoded rules

import re
import json
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from openai import OpenAI

# Initialize OpenAI client
try:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Warning: OPENAI_API_KEY not found. GPT analysis will use fallback mode.")
        client = None
    else:
        client = OpenAI(api_key=api_key)
except Exception as e:
    print(f"Warning: Failed to initialize OpenAI client: {e}. GPT analysis will use fallback mode.")
    client = None

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

class SkillLevel(Enum):
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate" 
    ADVANCED = "Advanced"
    EXPERT = "Expert"

class EvidenceType(Enum):
    COURSEWORK = "coursework"
    PROJECT = "project"
    WORK_EXPERIENCE = "work_experience"
    CERTIFICATION = "certification"
    OPTIMIZATION = "optimization"
    LEADERSHIP = "leadership"

@dataclass
class SkillEvidence:
    skill_name: str
    evidence_text: str
    evidence_type: EvidenceType
    context: str
    proficiency_score: int  # 0-100
    transferability_score: int  # 0-100
    depth_indicators: List[str]
    
@dataclass
class SoftSkillEvidence:
    skill_name: str
    evidence_sentences: List[str]
    confidence_score: int  # 0-100
    supporting_context: str

@dataclass
class JobFitAnalysis:
    overall_fit: str  # Professional hiring summary (2-4 paragraphs)
    requirement_breakdown: List[Dict]  # Skill-by-skill comparison table
    strengths_for_role: List[str]  # Technical and soft strengths with evidence
    gaps_to_address: List[str]  # Missing/weak skills with recommendations
    hiring_decision: str  # Hire/Interview/No Hire
    recommendation: str  # 1-2 paragraph explanation of decision
    interview_focus_areas: List[str]  # 4-6 focus points for interviews
    overall_score: int  # 0-100% match percentage

@dataclass
class EnhancedCVAnalysis:
    candidate_name: str
    primary_role: str
    experience_years: float
    technical_skills: List[SkillEvidence]
    soft_skills: List[SoftSkillEvidence]
    portfolio_links: List[str]
    certifications: List[Dict]
    career_progression: List[Dict]
    strengths: List[str]
    improvement_suggestions: List[str]
    ai_insights: str
    job_fit_analysis: Optional[JobFitAnalysis] = None

class GPTCVAnalyzer:
    def __init__(self):
        """Initialize GPT-powered CV analyzer with comprehensive skills taxonomy"""
        
        # Comprehensive skills taxonomy extracted from main.py
        self.technical_skills_taxonomy = {
            # Frontend Technologies
            "JavaScript": {"category": "frontend", "level": "Expert", "keywords": ["javascript", "js", "ecmascript"]},
            "TypeScript": {"category": "frontend", "level": "Advanced", "keywords": ["typescript", "ts"]},
            "React": {"category": "frontend", "level": "Expert", "keywords": ["react", "reactjs", "jsx"]},
            "Angular": {"category": "frontend", "level": "Expert", "keywords": ["angular", "angularjs"]},
            "Vue.js": {"category": "frontend", "level": "Expert", "keywords": ["vue", "vuejs", "vue.js"]},
            "React Native": {"category": "mobile", "level": "Advanced", "keywords": ["react native", "react-native"]},
            "JSX": {"category": "frontend", "level": "Intermediate", "keywords": ["jsx"]},
            "HTML5": {"category": "frontend", "level": "Advanced", "keywords": ["html5", "html"]},
            "CSS3": {"category": "frontend", "level": "Advanced", "keywords": ["css3", "css"]},
            "Sass/SCSS": {"category": "frontend", "level": "Advanced", "keywords": ["sass", "scss"]},
            "Less": {"category": "frontend", "level": "Intermediate", "keywords": ["less"]},
            "Styled Components": {"category": "frontend", "level": "Advanced", "keywords": ["styled-components", "styled components"]},
            
            # CSS Frameworks
            "Tailwind CSS": {"category": "frontend", "level": "Advanced", "keywords": ["tailwind", "tailwindcss"]},
            "Bootstrap": {"category": "frontend", "level": "Advanced", "keywords": ["bootstrap"]},
            "Material-UI": {"category": "frontend", "level": "Intermediate", "keywords": ["material-ui", "mui"]},
            "Chakra UI": {"category": "frontend", "level": "Intermediate", "keywords": ["chakra ui", "chakra-ui"]},
            
            # State Management
            "Redux": {"category": "frontend", "level": "Advanced", "keywords": ["redux"]},
            "MobX": {"category": "frontend", "level": "Intermediate", "keywords": ["mobx"]},
            "Zustand": {"category": "frontend", "level": "Intermediate", "keywords": ["zustand"]},
            "Context API": {"category": "frontend", "level": "Advanced", "keywords": ["context api", "react context"]},
            "Recoil": {"category": "frontend", "level": "Intermediate", "keywords": ["recoil"]},
            "State Management": {"category": "frontend", "level": "Advanced", "keywords": ["state management"]},
            
            # Backend Technologies
            "Node.js": {"category": "backend", "level": "Expert", "keywords": ["node.js", "nodejs", "node"]},
            "Python": {"category": "backend", "level": "Expert", "keywords": ["python"]},
            "Java": {"category": "backend", "level": "Expert", "keywords": ["java"]},
            "PHP": {"category": "backend", "level": "Intermediate", "keywords": ["php"]},
            "Spring Boot": {"category": "backend", "level": "Advanced", "keywords": ["spring boot", "spring"]},
            "Django": {"category": "backend", "level": "Advanced", "keywords": ["django"]},
            "Flask": {"category": "backend", "level": "Advanced", "keywords": ["flask"]},
            "Express.js": {"category": "backend", "level": "Advanced", "keywords": ["express.js", "express", "expressjs"]},
            "FastAPI": {"category": "backend", "level": "Advanced", "keywords": ["fastapi"]},
            
            # Databases
            "SQL": {"category": "database", "level": "Advanced", "keywords": ["sql"]},
            "PostgreSQL": {"category": "database", "level": "Advanced", "keywords": ["postgresql", "postgres"]},
            "MySQL": {"category": "database", "level": "Advanced", "keywords": ["mysql"]},
            "MongoDB": {"category": "database", "level": "Intermediate", "keywords": ["mongodb", "mongo"]},
            "NoSQL": {"category": "database", "level": "Intermediate", "keywords": ["nosql"]},
            "Redis": {"category": "database", "level": "Intermediate", "keywords": ["redis"]},
            "Database Management": {"category": "database", "level": "Advanced", "keywords": ["database management", "db management"]},
            
            # APIs & Web Services
            "REST APIs": {"category": "api", "level": "Advanced", "keywords": ["rest api", "rest", "restful"]},
            "GraphQL": {"category": "api", "level": "Intermediate", "keywords": ["graphql"]},
            "API Development": {"category": "api", "level": "Expert", "keywords": ["api development", "api design"]},
            
            # Testing
            "Jest": {"category": "testing", "level": "Advanced", "keywords": ["jest"]},
            "Cypress": {"category": "testing", "level": "Advanced", "keywords": ["cypress"]},
            "Selenium": {"category": "testing", "level": "Intermediate", "keywords": ["selenium"]},
            "Mocha": {"category": "testing", "level": "Intermediate", "keywords": ["mocha"]},
            "Chai": {"category": "testing", "level": "Intermediate", "keywords": ["chai"]},
            "Puppeteer": {"category": "testing", "level": "Intermediate", "keywords": ["puppeteer"]},
            "Unit Testing": {"category": "testing", "level": "Advanced", "keywords": ["unit testing", "unit test"]},
            "Integration Testing": {"category": "testing", "level": "Intermediate", "keywords": ["integration testing", "integration test"]},
            "E2E Testing": {"category": "testing", "level": "Advanced", "keywords": ["e2e testing", "end to end testing"]},
            "Test Driven Development": {"category": "testing", "level": "Intermediate", "keywords": ["tdd", "test driven development"]},
            "Testing": {"category": "testing", "level": "Intermediate", "keywords": ["testing"]},
            
            # Build Tools & DevOps
            "Webpack": {"category": "build", "level": "Advanced", "keywords": ["webpack"]},
            "Vite": {"category": "build", "level": "Advanced", "keywords": ["vite"]},
            "Rollup": {"category": "build", "level": "Intermediate", "keywords": ["rollup"]},
            "Parcel": {"category": "build", "level": "Intermediate", "keywords": ["parcel"]},
            "Babel": {"category": "build", "level": "Advanced", "keywords": ["babel"]},
            "ESLint": {"category": "build", "level": "Advanced", "keywords": ["eslint"]},
            "Prettier": {"category": "build", "level": "Intermediate", "keywords": ["prettier"]},
            "Build Tools": {"category": "build", "level": "Intermediate", "keywords": ["build tools"]},
            
            # DevOps & Infrastructure
            "Git": {"category": "devops", "level": "Advanced", "keywords": ["git"]},
            "Docker": {"category": "devops", "level": "Intermediate", "keywords": ["docker"]},
            "CI/CD": {"category": "devops", "level": "Intermediate", "keywords": ["ci/cd", "continuous integration", "continuous deployment"]},
            "AWS": {"category": "cloud", "level": "Intermediate", "keywords": ["aws", "amazon web services"]},
            "Linux": {"category": "devops", "level": "Intermediate", "keywords": ["linux"]},
            "DevOps": {"category": "devops", "level": "Basic", "keywords": ["devops"]},
            "Server Architecture": {"category": "backend", "level": "Advanced", "keywords": ["server architecture"]},
            
            # CMS & E-commerce
            "Shopify": {"category": "cms", "level": "Advanced", "keywords": ["shopify"]},
            "Liquid": {"category": "cms", "level": "Advanced", "keywords": ["liquid"]},
            "WordPress": {"category": "cms", "level": "Advanced", "keywords": ["wordpress"]},
            "Drupal": {"category": "cms", "level": "Advanced", "keywords": ["drupal"]},
            "Joomla": {"category": "cms", "level": "Intermediate", "keywords": ["joomla"]},
            "Magento": {"category": "cms", "level": "Advanced", "keywords": ["magento"]},
            
            # Design & UX
            "Responsive Design": {"category": "design", "level": "Advanced", "keywords": ["responsive design", "responsive"]},
            "Web Performance": {"category": "performance", "level": "Intermediate", "keywords": ["web performance", "performance optimization"]},
            "Web Security": {"category": "security", "level": "Intermediate", "keywords": ["web security", "security"]},
            
            # Programming Fundamentals
            "Programming Fundamentals": {"category": "core", "level": "Expert", "keywords": ["programming", "coding"]},
            "Agile": {"category": "methodology", "level": "Intermediate", "keywords": ["agile", "scrum"]},
        }
        
        # Soft skills taxonomy
        self.soft_skills_taxonomy = {
            "Communication": {"keywords": ["communication", "presenting", "documented", "collaborated", "stakeholder"]},
            "Problem Solving": {"keywords": ["problem solving", "solved", "resolved", "troubleshoot", "debugging"]},
            "Collaboration": {"keywords": ["collaboration", "team work", "cross-functional", "worked with"]},
            "Leadership": {"keywords": ["leadership", "led", "managed", "supervised", "mentored", "guided"]},
            "Analytical Thinking": {"keywords": ["analytical", "analyzed", "evaluated", "assessed", "data-driven"]},
            "Project Management": {"keywords": ["project management", "coordinated", "planned", "organized"]},
            "Time Management": {"keywords": ["time management", "prioritized", "deadlines", "scheduling"]},
            "Adaptability": {"keywords": ["adaptability", "flexible", "learning", "adjusting"]},
            "Critical Thinking": {"keywords": ["critical thinking", "evaluated", "reasoned", "logical"]},
            "Creativity": {"keywords": ["creativity", "innovative", "creative", "designed", "brainstormed"]},
        }
        
        # Job roles and their typical skill requirements
        self.job_roles_taxonomy = {
            "Frontend Engineer": ["JavaScript", "TypeScript", "React", "Angular", "Vue.js", "HTML5", "CSS3", "Responsive Design"],
            "Backend Engineer": ["Node.js", "Python", "Java", "API Development", "Database Management", "SQL"],
            "Full Stack Engineer": ["JavaScript", "TypeScript", "React", "Node.js", "Python", "REST APIs", "Database Management"],
            "Software Engineer": ["Programming Fundamentals", "Problem Solving", "Git", "Testing"],
            "DevOps Engineer": ["Docker", "CI/CD", "AWS", "Linux", "Git"],
            "Mobile Developer": ["React Native", "JavaScript", "API Development"],
        }

    def analyze_cv_comprehensive(self, cv_text: str, job_description: str = None) -> EnhancedCVAnalysis:
        """GPT-powered comprehensive CV analysis"""
        
        try:
            # Single GPT call to analyze the entire CV comprehensively
            analysis_result = self._analyze_cv_with_gpt(cv_text, job_description)
            return analysis_result
            
        except Exception as e:
            # Fallback to basic analysis if GPT fails
            print(f"GPT analysis failed: {e}")
            return self._fallback_analysis(cv_text, job_description)

    def _analyze_cv_with_gpt(self, cv_text: str, job_description: Optional[str] = None) -> EnhancedCVAnalysis:
        """Use GPT to perform comprehensive CV analysis"""
        
        # Create the system prompt for CV analysis with skills taxonomy
        skills_list = list(self.technical_skills_taxonomy.keys())[:50]  # First 50 skills
        soft_skills_list = list(self.soft_skills_taxonomy.keys())
        
        system_prompt = f"""You are an expert HR professional and technical recruiter with 15+ years of experience in hiring for technology roles. You specialize in comprehensive CV analysis and job fit assessment.

Your task is to analyze CVs with the expertise of a senior hiring manager, providing detailed, actionable insights that would be used in real hiring decisions.

SKILLS REFERENCE TAXONOMY:
Technical Skills to look for: {', '.join(skills_list)}
Soft Skills to identify: {', '.join(soft_skills_list)}

Use this taxonomy as a reference but don't limit yourself to only these skills. Extract any relevant skills mentioned in the CV.

You must respond with a valid JSON object that exactly matches this structure - do not add any extra fields or modify the format:

{
  "candidate_name": "string",
  "primary_role": "string", 
  "experience_years": number,
  "technical_skills": [
    {
      "skill_name": "string",
      "evidence_text": "string",
      "evidence_type": "work_experience",
      "context": "string",
      "proficiency_score": number,
      "transferability_score": number,
      "depth_indicators": ["string"]
    }
  ],
  "soft_skills": [
    {
      "skill_name": "string", 
      "evidence_sentences": ["string"],
      "confidence_score": number,
      "supporting_context": "string"
    }
  ],
  "portfolio_links": ["string"],
  "certifications": [{"name": "string", "issuer": "string", "year": "string"}],
  "career_progression": [{"role": "string", "company": "string", "duration": "string", "key_achievements": ["string"]}],
  "strengths": ["string"],
  "improvement_suggestions": ["string"],
  "ai_insights": "string",
  "job_fit_analysis": {
    "overall_fit": "string",
    "requirement_breakdown": [{"skill": "string", "required": "string", "candidate_level": "string", "evidence": "string", "score": number}],
    "strengths_for_role": ["string"],
    "gaps_to_address": ["string"], 
    "hiring_decision": "string",
    "recommendation": "string",
    "interview_focus_areas": ["string"],
    "overall_score": number
  }
}

IMPORTANT INSTRUCTIONS:
- For evidence_type, only use: "work_experience", "project", "certification", or "coursework"
- For hiring_decision, only use: "Hire", "Interview", or "No Hire"
- All scores should be integers between 0-100
- Provide realistic, evidence-based analysis
- Extract concrete technical skills with specific evidence from the CV
- Identify soft skills only when there's clear evidence
- If no job description is provided, set job_fit_analysis to null
- Be thorough but concise in your analysis

SCORING GUIDELINES:
- Proficiency Score (0-100): Based on depth of experience and context
  * 90-100: Expert level with leadership/architecture experience
  * 70-89: Advanced with commercial experience
  * 50-69: Intermediate with project experience
  * 30-49: Basic with coursework/learning experience
  * 0-29: Minimal or no evidence

- Transferability Score (0-100): How transferable the skill is to other roles
  * Related technologies get higher transferability scores
  * Core programming languages: 85-95
  * Frameworks: 60-80
  * Specific tools: 40-60

EVIDENCE EXTRACTION:
- Always provide specific evidence from the CV text
- Quote relevant experience, projects, or achievements
- Context should explain where/how the skill was used
- Depth indicators should reflect the level of involvement
"""

        # Create the user prompt
        user_prompt = f"""Please analyze this CV comprehensively:

CV CONTENT:
{cv_text}

"""
        
        if job_description:
            user_prompt += f"""
JOB DESCRIPTION:
{job_description}

Please include detailed job fit analysis comparing the candidate's qualifications against the job requirements.
"""
        else:
            user_prompt += "No specific job description provided - perform general CV analysis only (set job_fit_analysis to null)."

        try:
            if not client:
                raise Exception("OpenAI client not available")
                
            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=4000
            )
            
            # Parse the JSON response
            analysis_json = json.loads(response.choices[0].message.content)
            
            # Convert to our data structures
            technical_skills = [
                SkillEvidence(
                    skill_name=skill["skill_name"],
                    evidence_text=skill["evidence_text"],
                    evidence_type=EvidenceType(skill["evidence_type"]),
                    context=skill["context"],
                    proficiency_score=skill["proficiency_score"],
                    transferability_score=skill["transferability_score"],
                    depth_indicators=skill["depth_indicators"]
                ) for skill in analysis_json["technical_skills"]
            ]
            
            soft_skills = [
                SoftSkillEvidence(
                    skill_name=skill["skill_name"],
                    evidence_sentences=skill["evidence_sentences"],
                    confidence_score=skill["confidence_score"],
                    supporting_context=skill["supporting_context"]
                ) for skill in analysis_json["soft_skills"]
            ]
            
            # Handle job fit analysis
            job_fit_analysis = None
            if analysis_json.get("job_fit_analysis") and job_description:
                jfa_data = analysis_json["job_fit_analysis"]
                job_fit_analysis = JobFitAnalysis(
                    overall_fit=jfa_data["overall_fit"],
                    requirement_breakdown=jfa_data["requirement_breakdown"],
                    strengths_for_role=jfa_data["strengths_for_role"],
                    gaps_to_address=jfa_data["gaps_to_address"],
                    hiring_decision=jfa_data["hiring_decision"],
                    recommendation=jfa_data["recommendation"],
                    interview_focus_areas=jfa_data["interview_focus_areas"],
                    overall_score=jfa_data["overall_score"]
                )
            
            return EnhancedCVAnalysis(
                candidate_name=analysis_json["candidate_name"],
                primary_role=analysis_json["primary_role"],
                experience_years=analysis_json["experience_years"],
                technical_skills=technical_skills,
                soft_skills=soft_skills,
                portfolio_links=analysis_json["portfolio_links"],
                certifications=analysis_json["certifications"],
                career_progression=analysis_json["career_progression"],
                strengths=analysis_json["strengths"],
                improvement_suggestions=analysis_json["improvement_suggestions"],
                ai_insights=analysis_json["ai_insights"],
                job_fit_analysis=job_fit_analysis
            )
            
        except json.JSONDecodeError as e:
            print(f"Failed to parse GPT response as JSON: {e}")
            raise
        except Exception as e:
            print(f"GPT analysis error: {e}")
            raise

    def _fallback_analysis(self, cv_text: str, job_description: Optional[str] = None) -> EnhancedCVAnalysis:
        """Simple fallback analysis when GPT fails"""
        
        # Extract basic info with simple regex
        lines = cv_text.split('\n')
        candidate_name = "Candidate"
        
        # Try to find name in first few lines
        for line in lines[:5]:
            if len(line.strip()) > 0 and '@' not in line and '+' not in line:
                words = line.strip().split()
                if len(words) >= 2 and all(word.isalpha() for word in words[:2]):
                    candidate_name = ' '.join(words[:2])
                    break
        
        # Basic technical skills extraction
        tech_keywords = ['python', 'javascript', 'react', 'node', 'sql', 'html', 'css', 'java', 'c++', 'golang']
        technical_skills = []
        
        cv_lower = cv_text.lower()
        for keyword in tech_keywords:
            if keyword in cv_lower:
                technical_skills.append(
                    SkillEvidence(
                        skill_name=keyword.title(),
                        evidence_text=f"Mentioned in CV: {keyword}",
                        evidence_type=EvidenceType.WORK_EXPERIENCE,
                        context="General CV mention",
                        proficiency_score=50,
                        transferability_score=60,
                        depth_indicators=["mentioned"]
                    )
                )
        
        return EnhancedCVAnalysis(
            candidate_name=candidate_name,
            primary_role="Software Developer",
            experience_years=2.0,
            technical_skills=technical_skills,
            soft_skills=[],
            portfolio_links=[],
            certifications=[],
            career_progression=[],
            strengths=["Technical background"],
            improvement_suggestions=["Expand technical skills", "Add more project details"],
            ai_insights="Basic CV analysis - GPT analysis unavailable",
            job_fit_analysis=None
        )

    def match_with_job_description(self, cv_analysis: EnhancedCVAnalysis, job_description: str) -> Dict:
        """Generate job matching results - compatibility method for existing API"""
        
        # If we already have job fit analysis, use that
        if cv_analysis.job_fit_analysis:
            return {
                "overall_match_score": cv_analysis.job_fit_analysis.overall_score,
                "technical_match": cv_analysis.job_fit_analysis.overall_score,
                "soft_skills_match": min(85, cv_analysis.job_fit_analysis.overall_score + 10),
                "experience_match": cv_analysis.job_fit_analysis.overall_score,
                "recommendations": cv_analysis.job_fit_analysis.recommendation,
                "key_strengths": cv_analysis.job_fit_analysis.strengths_for_role,
                "skill_gaps": cv_analysis.job_fit_analysis.gaps_to_address,
                "hiring_decision": cv_analysis.job_fit_analysis.hiring_decision
            }
        
        # Otherwise, run a fresh analysis
        try:
            fresh_analysis = self._analyze_cv_with_gpt(cv_analysis.candidate_name, job_description)
            if fresh_analysis.job_fit_analysis:
                return {
                    "overall_match_score": fresh_analysis.job_fit_analysis.overall_score,
                    "technical_match": fresh_analysis.job_fit_analysis.overall_score,
                    "soft_skills_match": min(85, fresh_analysis.job_fit_analysis.overall_score + 10),
                    "experience_match": fresh_analysis.job_fit_analysis.overall_score,
                    "recommendations": fresh_analysis.job_fit_analysis.recommendation,
                    "key_strengths": fresh_analysis.job_fit_analysis.strengths_for_role,
                    "skill_gaps": fresh_analysis.job_fit_analysis.gaps_to_address,
                    "hiring_decision": fresh_analysis.job_fit_analysis.hiring_decision
                }
        except:
            pass
            
        # Fallback basic matching
        return {
            "overall_match_score": 60,
            "technical_match": 60,
            "soft_skills_match": 65,
            "experience_match": 55,
            "recommendations": "General match - detailed analysis unavailable",
            "key_strengths": cv_analysis.strengths,
            "skill_gaps": cv_analysis.improvement_suggestions,
            "hiring_decision": "Interview"
        }
