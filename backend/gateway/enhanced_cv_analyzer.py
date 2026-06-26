# GPT-Powered CV Analysis System
# This module implements CV analysis using OpenAI GPT instead of hardcoded rules

import re
import json
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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

# Role-based skill weighting configuration
ROLE_SKILL_WEIGHTS = {
    "frontend": {
        "JavaScript": 25, "React": 20, "HTML/CSS": 15, "TypeScript": 15,
        "State Management": 10, "Responsive Design": 8, "Testing": 5, "DevOps": 2
    },
    "backend": {
        "Python": 25, "Node.js": 20, "Database Design": 15, "API Development": 15,
        "System Architecture": 10, "Security": 8, "Testing": 5, "DevOps": 2
    },
    "fullstack": {
        "JavaScript": 20, "React": 15, "Python": 15, "Node.js": 15,
        "Database Design": 10, "API Development": 10, "System Architecture": 8, 
        "Testing": 4, "DevOps": 3
    },
    "devops": {
        "Docker": 20, "Kubernetes": 18, "AWS": 15, "CI/CD": 15,
        "Linux": 12, "Monitoring": 10, "Security": 8, "Scripting": 2
    },
    "default": {
        # Equal weighting fallback
        "default_weight": 10
    }
}

# Match quality labels based on weighted scores
MATCH_QUALITY_LABELS = {
    (90, 100): {"label": "Excellent Match", "color": "emerald", "icon": "🌟"},
    (80, 89): {"label": "Very Strong Match", "color": "green", "icon": "✨"},
    (70, 79): {"label": "Strong Match", "color": "blue", "icon": "💪"},
    (60, 69): {"label": "Good Match", "color": "yellow", "icon": "👍"},
    (50, 59): {"label": "Moderate Match", "color": "orange", "icon": "🤔"},
    (0, 49): {"label": "Weak Match", "color": "red", "icon": "❌"}
}

# Hiring decision thresholds
HIRING_THRESHOLDS = {
    (85, 100): "High Priority Hire",
    (75, 84): "Strong Hire", 
    (65, 74): "Potential Fit - Needs Development",
    (0, 64): "Not Recommended"
}

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
    evidence_sentences: List[str]  # Specific CV sentences supporting this skill
    skill_weight: float  # Role-based importance weight (0-100)
    weighted_score: float  # proficiency_score * (skill_weight / 100)
    portfolio_links: List[str]  # Related GitHub/portfolio links
    
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

def get_role_skill_weights(role: str) -> Dict[str, float]:
    """Get skill weights for a specific role"""
    role_key = role.lower().replace(" ", "").replace("-", "")
    
    if "frontend" in role_key or "react" in role_key or "ui" in role_key:
        return ROLE_SKILL_WEIGHTS["frontend"]
    elif "backend" in role_key or "api" in role_key or "server" in role_key:
        return ROLE_SKILL_WEIGHTS["backend"]
    elif "fullstack" in role_key or "full-stack" in role_key:
        return ROLE_SKILL_WEIGHTS["fullstack"]
    elif "devops" in role_key or "infrastructure" in role_key:
        return ROLE_SKILL_WEIGHTS["devops"]
    else:
        return ROLE_SKILL_WEIGHTS["default"]

def calculate_weighted_score(skills: List[SkillEvidence]) -> float:
    """Calculate weighted overall score based on skill importance"""
    if not skills:
        return 0.0
    
    total_weighted_score = sum(skill.weighted_score for skill in skills)
    total_weight = sum(skill.skill_weight for skill in skills)
    
    if total_weight == 0:
        return sum(skill.proficiency_score for skill in skills) / len(skills)
    
    return (total_weighted_score / total_weight) * 100

def get_match_quality_label(score: float) -> Dict[str, str]:
    """Get match quality label and styling based on score"""
    for (min_score, max_score), quality_info in MATCH_QUALITY_LABELS.items():
        if min_score <= score <= max_score:
            return quality_info
    return MATCH_QUALITY_LABELS[(0, 49)]  # Default to weak match

def get_hiring_decision(score: float) -> str:
    """Get hiring decision based on weighted score"""
    for (min_score, max_score), decision in HIRING_THRESHOLDS.items():
        if min_score <= score <= max_score:
            return decision
    return "Not Recommended"

def extract_portfolio_links(cv_text: str) -> List[Dict[str, str]]:
    """Extract portfolio, GitHub, LinkedIn links from CV"""
    links = []
    
    # GitHub patterns
    github_pattern = r'(?:github\.com/|@github:|github:)\s*([^\s\n]+)'
    github_matches = re.findall(github_pattern, cv_text, re.IGNORECASE)
    for match in github_matches:
        links.append({
            "type": "github",
            "url": f"https://github.com/{match.strip('/')}" if not match.startswith('http') else match,
            "icon": "fab fa-github",
            "label": "GitHub"
        })
    
    # LinkedIn patterns
    linkedin_pattern = r'(?:linkedin\.com/in/|@linkedin:|linkedin:)\s*([^\s\n]+)'
    linkedin_matches = re.findall(linkedin_pattern, cv_text, re.IGNORECASE)
    for match in linkedin_matches:
        links.append({
            "type": "linkedin", 
            "url": f"https://linkedin.com/in/{match.strip('/')}" if not match.startswith('http') else match,
            "icon": "fab fa-linkedin",
            "label": "LinkedIn"
        })
    
    # Portfolio/Website patterns
    website_pattern = r'(?:portfolio|website|site):\s*(https?://[^\s\n]+)'
    website_matches = re.findall(website_pattern, cv_text, re.IGNORECASE)
    for match in website_matches:
        links.append({
            "type": "portfolio",
            "url": match,
            "icon": "fas fa-globe",
            "label": "Portfolio"
        })
    
    return links

class GPTCVAnalyzer:
    def __init__(self):
        """Initialize GPT-powered CV analyzer"""
        pass

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
        
        # Create the system prompt for CV analysis
        system_prompt = """You are an expert HR professional and technical recruiter with 15+ years of experience in hiring for technology roles. You specialize in comprehensive CV analysis and job fit assessment.

Your task is to analyze CVs with the expertise of a senior hiring manager, providing detailed, actionable insights that would be used in real hiring decisions.

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
      "depth_indicators": ["string"],
      "evidence_sentences": ["string"],
      "skill_weight": number,
      "weighted_score": number,
      "portfolio_links": ["string"]
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

CRITICAL EXTRACTION REQUIREMENTS:

🔍 CERTIFICATIONS - Extract ALL certificates, credentials, qualifications:
- Look for course completions, professional certifications, licenses
- Examples: "Meta Front-End Developer Certificate", "AWS Cloud Practitioner", "Google Analytics"
- Include issuer (Coursera, AWS, Google) and year if mentioned
- DO NOT leave certifications array empty if ANY are mentioned in CV
- If certifications section appears empty, actively search for online courses, certificates, or qualifications

🔗 PORTFOLIO LINKS - Extract ALL online profiles and portfolios:
- GitHub profiles: github.com/username
- LinkedIn profiles: linkedin.com/in/username  
- Personal websites, portfolio sites, project demos
- Social media profiles relevant to profession
- DO NOT leave portfolio_links empty if URLs/profiles are mentioned
- If no explicit URLs found, look for GitHub usernames, LinkedIn mentions, or portfolio references

💼 CAREER PROGRESSION - Use EXACT company names and dates from CV:
- Do NOT use generic names like "Tech Solutions Inc."
- Use actual company names: "TechFlow Inc.", "BrightApps", etc.
- Extract precise durations: "2021-present", "2019-2020"
- Include key achievements with QUANTIFIED OUTCOMES whenever possible
- Focus on measurable impact: "improved performance by 30%", "mentored 3 developers"

⚙️ TECHNICAL SKILLS - Enhanced Evidence Mapping & Weighting:
- RESPONSIVE DESIGN: Look for "mobile", "conversion", "responsive", "bootstrap", "mobile-first" (Weight: 8)
- STATE MANAGEMENT: Look for "Redux", "MobX", "state", "store", "context" (Weight: 10-15)  
- WEB PERFORMANCE: Look for "speed", "performance", "optimization", "load times", "bundle size" (Weight: 8)
- TDD: Look for "test", "testing", "coverage", "unit tests", "jest", "cypress" (Weight: 5)
- BUILD TOOLS: Look for "webpack", "vite", "build", "bundling", "CI/CD", "pipeline" (Weight: 2-5)
- JAVASCRIPT: Look for "JavaScript", "ES6+", "DOM", "async/await", "promises" (Weight: 20-25)
- REACT: Look for "React", "components", "hooks", "JSX", "virtual DOM" (Weight: 15-20)
- NODE.JS: Look for "Node.js", "Express", "npm", "server-side" (Weight: 15-20)
- PYTHON: Look for "Python", "Django", "Flask", "pandas", "FastAPI" (Weight: 20-25)
- DATABASE: Look for "SQL", "MongoDB", "PostgreSQL", "database design" (Weight: 10-15)

🏷️ ROLE-BASED SKILL WEIGHTING:
- Frontend Roles: JavaScript (25%), React (20%), HTML/CSS (15%), TypeScript (15%)
- Backend Roles: Python/Node.js (25%), Database (15%), API Development (15%), Architecture (10%)
- Full-Stack Roles: Balanced weights across frontend/backend skills
- DevOps Roles: Docker (20%), Kubernetes (18%), AWS (15%), CI/CD (15%)

📋 EVIDENCE_SENTENCES EXTRACTION:
- Extract 2-4 specific CV sentences that directly support each skill
- Include quantifiable achievements: "boosted mobile conversion by 18%"
- Include project descriptions: "built responsive e-commerce platform"
- Include technical implementations: "implemented Redux state management"

💪 EVIDENCE MAPPING EXAMPLES:
- "boosted mobile conversion by 18%" → Responsive Design (Expert 90%)
- "improved speed 30%, reduced load times 40%" → Web Performance (Expert 95%)
- "test coverage +40%" → TDD (Advanced 80%)
- "mentored juniors, led Agile ceremonies" → Leadership (Advanced 85%)
- "Redux experience" → State Management (Advanced 85%)
- "Webpack, GitLab CI/CD, Docker" → Build Tools & DevOps (Advanced 80%)
- "5 years React development" → React (Expert 90%)
- "Built REST APIs" → API Development (Advanced 85%)
- Simply mentioning "HTML, CSS, JavaScript" → Each gets (Intermediate 75%)
- Work experience with technology → Minimum (Advanced 80%)

📊 ENHANCED SCORING & WEIGHTING ALGORITHM:
- NEVER mark as "No evidence" if any related terms found in CV
- Look for implicit evidence: performance improvements = web performance skills
- START with 70% as minimum for any mentioned skill
- Quantified achievements should boost scores to 85-95%
- Skills with measurable results or years of experience: 85-95%
- Skills explicitly mentioned with context: 75-85%
- Skills mentioned in job titles or work descriptions: 80-90%
- DO NOT give scores below 65% if skill is clearly present in CV
- Target realistic 85-95% match when candidate shows strong evidence
- BE GENEROUS with scoring when evidence is present - err on the higher side

🧮 WEIGHTED SCORE CALCULATION:
- skill_weight: Use role-appropriate weights (JavaScript=25 for frontend, Python=25 for backend)
- weighted_score: proficiency_score * (skill_weight / 100)
- Example: JavaScript with 85% proficiency and 25% weight = 85 * 0.25 = 21.25
- Higher weights for core skills, lower for supportive skills

🎯 JOB FIT ANALYSIS (when job description provided):
- Focus on closing the gap between candidate and JD requirements
- Highlight implicit skills (e.g., performance optimization implies advanced React knowledge)
- Emphasize security and DevOps experience when present
- Give specific, actionable interview focus areas
- Provide realistic but optimistic assessment when skills align well

QUALITY STANDARDS:
- Use exact quotes from CV for evidence_text with context
- MANDATORY SCORING GUIDELINES:
  * 85-100: Expert with proven results, quantified achievements, or extensive experience
  * 75-89: Advanced with specific implementations, projects, or clear usage examples
  * 70-79: Intermediate with some experience or mentions in job descriptions
  * 65-74: Basic/Beginner level but clearly mentioned in CV
  * NEVER score below 65% if skill appears anywhere in CV
- BE GENEROUS: If a candidate lists a skill, they likely have practical experience - score accordingly
- Prioritize job-critical skills in technical_skills array (React, TypeScript, etc. first)
- Include quantified achievements in soft_skills supporting_context
- Fill ALL sections - no empty arrays unless truly no evidence exists
- Provide actionable, specific insights focused on role alignment
- Weight recent experience and relevant projects higher in scoring
- IMPORTANT: Aim for realistic but optimistic scoring to reflect candidate strengths

🔧 JSON FORMATTING REQUIREMENTS:
- Always properly escape quotes in strings with \\
- Never leave strings unterminated
- End all arrays and objects properly with closing braces/brackets  
- No trailing commas before closing braces
- Use double quotes for all JSON keys and string values
- Ensure all strings are properly closed

📈 SCORING EXAMPLES FOR CLARITY:
- "5+ years React experience, built e-commerce platform" → proficiency_score: 85-95
- "Led team of developers, mentored juniors" → proficiency_score: 90-95  
- "Optimized performance by 40%, reduced load time" → proficiency_score: 80-90
- "Built RESTful APIs, integrated third-party services" → proficiency_score: 75-85
- "Experience with JavaScript, worked on various projects" → proficiency_score: 70-80
- "Familiar with Python, basic scripting" → proficiency_score: 65-70
Remember: Professional developers typically score 75+ on their primary skills!"""

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
                    depth_indicators=skill["depth_indicators"],
                    evidence_sentences=skill["evidence_sentences"],
                    skill_weight=skill["skill_weight"],
                    weighted_score=skill["weighted_score"],
                    portfolio_links=skill["portfolio_links"]
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
            response_text = response.choices[0].message.content
            print(f"Response text: {response_text[:500]}...")
            # Try to fix common JSON issues
            try:
                # Remove trailing commas and fix unterminated strings
                cleaned_response = response_text.strip()
                cleaned_response = re.sub(r',\s*([}\]])', r'\1', cleaned_response)
                if cleaned_response.count('"') % 2 != 0:
                    cleaned_response += '"'
                analysis_json = json.loads(cleaned_response)
                print("Successfully fixed and parsed JSON response")
            except:
                print("Could not fix JSON, using fallback analysis")
                return self._fallback_analysis(cv_text, job_description)
        except Exception as e:
            print(f"GPT analysis error: {e}")
            return self._fallback_analysis(cv_text, job_description)

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
                skill_weight = 10.0  # Default weight for fallback
                proficiency_score = 50
                technical_skills.append(
                    SkillEvidence(
                        skill_name=keyword.title(),
                        evidence_text=f"Mentioned in CV: {keyword}",
                        evidence_type=EvidenceType.WORK_EXPERIENCE,
                        context="General CV mention",
                        proficiency_score=proficiency_score,
                        transferability_score=60,
                        depth_indicators=["mentioned"],
                        evidence_sentences=[f"Found reference to {keyword} in CV"],
                        skill_weight=skill_weight,
                        weighted_score=float(proficiency_score * (skill_weight / 100)),
                        portfolio_links=[]
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
