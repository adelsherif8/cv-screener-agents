# Enhanced CV Analysis System
# This module implements advanced CV-Job matching with GPT-powered analysis

import re
import json
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
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

class AdvancedCVAnalyzer:
    def __init__(self):
        """Initialize GPT-powered CV analyzer"""
        pass
        
        # Depth indicator keywords for skill levels
        self.depth_indicators = {
            SkillLevel.EXPERT: [
                "optimized", "scaled", "architected", "led", "designed", "implemented",
                "deployed", "performance", "production", "senior", "lead", "mentor",
                "technical decisions", "best practices", "code review"
            ],
            SkillLevel.ADVANCED: [
                "developed", "built", "integrated", "configured", "managed", "maintained",
                "troubleshoot", "debug", "testing", "ci/cd", "automated", "refactored"
            ],
            SkillLevel.INTERMEDIATE: [
                "worked with", "used", "familiar", "experience with", "knowledge of",
                "projects", "applications", "websites", "collaborated"
            ],
            SkillLevel.BEGINNER: [
                "coursework", "learned", "studied", "introduction", "basic", "fundamental",
                "tutorial", "bootcamp", "certification course"
            ]
        }
        
        # Soft skill indicators
        self.soft_skill_patterns = {
            "Leadership": [
                r"led (a )?team", r"managed \d+ (developers|people|team members)",
                r"mentored", r"guided", r"supervised", r"coordinated team"
            ],
            "Communication": [
                r"collaborated with", r"worked closely with", r"client communication",
                r"presented", r"documented", r"stakeholder"
            ],
            "Problem Solving": [
                r"debugged", r"troubleshoot", r"resolved", r"identified and fixed",
                r"optimized", r"improved performance", r"bottlenecks"
            ],
            "Project Management": [
                r"managed project", r"delivered on time", r"project timeline",
                r"coordinated", r"organized", r"planned"
            ],
            "Adaptability": [
                r"learned", r"adapted", r"transitioned", r"flexible",
                r"various technologies", r"different frameworks"
            ]
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
      "evidence_type": "work_experience|project|certification|coursework",
      "context": "string",
      "proficiency_score": number (0-100),
      "transferability_score": number (0-100),
      "depth_indicators": ["string"]
    }
  ],
  "soft_skills": [
    {
      "skill_name": "string", 
      "evidence_sentences": ["string"],
      "confidence_score": number (0-100),
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
    "hiring_decision": "Hire|Interview|No Hire",
    "recommendation": "string",
    "interview_focus_areas": ["string"],
    "overall_score": number (0-100)
  }
}

Guidelines:
- Extract exact technical skills mentioned with proficiency assessment
- Identify soft skills with concrete evidence from the CV
- Provide realistic experience calculations
- Give actionable improvement suggestions
- If job description provided, include comprehensive job fit analysis
- Use professional, hiring-manager tone
- Be objective and evidence-based"""

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
            user_prompt += "No specific job description provided - perform general CV analysis only."

        try:
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

    def _extract_candidate_name(self, cv_text: str) -> str:
        """Extract candidate name with proper capitalization"""
        # Look for name patterns at the beginning of CV
        lines = cv_text.split('\n')[:5]  # Check first 5 lines
        
        for line in lines:
            line = line.strip()
            # Skip email, phone, address patterns
            if '@' in line or '+' in line or 'phone' in line.lower():
                continue
                
            # Look for name-like patterns (2-4 words, no special chars except spaces)
            name_pattern = r'^([A-Z][a-z]+ [A-Z][a-z]+(?:\s[A-Z][a-z]+)?)(?:\s|$)'
            match = re.search(name_pattern, line, re.IGNORECASE)
            if match:
                return match.group(1).title()  # Proper case
                
        # Fallback: look for patterns like "Name: John Doe"
        name_patterns = [
            r'name[:\s]+([A-Z][a-z]+ [A-Z][a-z]+)',
            r'^([A-Z][a-z]+ [A-Z][a-z]+)\s+(?:resume|cv|engineer|developer)',
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, cv_text, re.IGNORECASE | re.MULTILINE)
            if match:
                return match.group(1).title()
                
        return "Unknown Candidate"

    def _extract_primary_role(self, cv_text: str) -> str:
        """Extract primary job role/title"""
        # Look for role indicators
        role_patterns = [
            r'(Front[- ]?End Engineer|Frontend Engineer|Front End Developer)',
            r'(Full[- ]?Stack Developer|Fullstack Developer)',
            r'(Software Engineer|Software Developer)',
            r'(Web Developer|Web Engineer)',
            r'(React Developer|JavaScript Developer)',
            r'(Backend Developer|Backend Engineer)',
            r'(DevOps Engineer|Cloud Engineer)',
            r'(Data Scientist|Data Engineer)',
            r'(Mobile Developer|iOS Developer|Android Developer)'
        ]
        
        for pattern in role_patterns:
            match = re.search(pattern, cv_text, re.IGNORECASE)
            if match:
                return match.group(1)
                
        return "Developer"

    def _calculate_experience_years(self, cv_text: str) -> float:
        """Calculate experience years from work history with improved accuracy"""
        work_periods = []
        
        # First try to find explicit experience statements
        experience_patterns = [
            r'(\d+)\+?\s*years?\s*of\s*experience',
            r'(\d+)\+?\s*years?\s*experience',
            r'experience.*?(\d+)\+?\s*years?',
            r'(\d+)\+?\s*years?\s*in\s*(software|development|programming)',
        ]
        
        for pattern in experience_patterns:
            matches = re.findall(pattern, cv_text, re.IGNORECASE)
            for match in matches:
                try:
                    years = int(match if isinstance(match, str) else match[0])
                    return float(years)
                except (ValueError, IndexError):
                    continue
        
        # Enhanced date pattern matching for work history
        date_patterns = [
            r'([A-Z][a-z]{2,8})\s+(\d{4})\s*[–-]\s*([A-Z][a-z]{2,8})\s+(\d{4})',  # Jan 2020 - Dec 2023
            r'(\d{1,2})/(\d{4})\s*[–-]\s*(\d{1,2})/(\d{4})',  # 01/2020 - 12/2023
            r'(\d{4})\s*[–-]\s*(\d{4})',  # 2020 - 2023
            r'(\d{4})\s*[–-]\s*(Present|Current|Now)',  # 2020 - Present
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, cv_text, re.IGNORECASE)
            for match in matches:
                try:
                    if len(match) == 4:  # Month Year - Month Year
                        start_year = int(match[1])
                        end_year = int(match[3]) if match[3].isdigit() else 2024
                        work_periods.append(end_year - start_year)
                    elif len(match) == 2:  # Year - Year
                        start_year = int(match[0])
                        end_year = int(match[1]) if match[1].isdigit() else 2024
                        work_periods.append(end_year - start_year)
                except (ValueError, IndexError):
                    continue
                    
        return sum(work_periods) if work_periods else 0.0

    def _analyze_technical_skills_with_context(self, cv_text: str) -> List[SkillEvidence]:
        """Advanced technical skill analysis with contextual evidence"""
        skills_evidence = []
        
        # Common technical skills to look for
        tech_skills = [
            "react", "vue", "angular", "javascript", "typescript", "node.js", "express",
            "python", "django", "flask", "fastapi", "java", "spring", "c++", "c#",
            "html", "css", "scss", "sass", "bootstrap", "tailwind", "mongodb", 
            "postgresql", "mysql", "redis", "docker", "kubernetes", "aws", "azure",
            "git", "github", "gitlab", "jenkins", "ci/cd", "testing", "jest", "cypress"
        ]
        
        for skill in tech_skills:
            evidence = self._find_skill_evidence(cv_text, skill)
            if evidence:
                skills_evidence.append(evidence)
                
        return skills_evidence

    def _find_skill_evidence(self, cv_text: str, skill: str) -> Optional[SkillEvidence]:
        """Find evidence for a specific skill with context analysis"""
        skill_pattern = re.compile(rf'\b{re.escape(skill)}(?:\.js)?\b', re.IGNORECASE)
        matches = []
        
        # Find all occurrences with surrounding context
        sentences = re.split(r'[.!?]+', cv_text)
        
        for sentence in sentences:
            if skill_pattern.search(sentence):
                matches.append(sentence.strip())
        
        if not matches:
            return None
            
        # Analyze the context to determine skill level
        all_evidence = ' '.join(matches)
        evidence_type = self._determine_evidence_type(all_evidence)
        proficiency_score = self._calculate_proficiency_score(all_evidence, skill)
        depth_indicators = self._extract_depth_indicators(all_evidence)
        skill_level = self._determine_skill_level(all_evidence, depth_indicators)
        
        # Calculate transferability
        transferability_score = 100  # Default for exact match
        
        return SkillEvidence(
            skill_name=skill.title(),
            evidence_text=matches[0][:200] + "..." if len(matches[0]) > 200 else matches[0],
            evidence_type=evidence_type,
            context=all_evidence[:300] + "..." if len(all_evidence) > 300 else all_evidence,
            proficiency_score=proficiency_score,
            transferability_score=transferability_score,
            depth_indicators=depth_indicators
        )

    def _determine_evidence_type(self, evidence_text: str) -> EvidenceType:
        """Determine the type of evidence for a skill"""
        text_lower = evidence_text.lower()
        
        if any(word in text_lower for word in ["coursework", "course", "studied", "learned"]):
            return EvidenceType.COURSEWORK
        elif any(word in text_lower for word in ["project", "built", "developed", "created"]):
            return EvidenceType.PROJECT
        elif any(word in text_lower for word in ["job", "work", "company", "role", "position"]):
            return EvidenceType.WORK_EXPERIENCE
        elif any(word in text_lower for word in ["certified", "certification", "certificate"]):
            return EvidenceType.CERTIFICATION
        elif any(word in text_lower for word in ["optimized", "improved", "enhanced", "performance"]):
            return EvidenceType.OPTIMIZATION
        elif any(word in text_lower for word in ["led", "managed", "mentored", "guided"]):
            return EvidenceType.LEADERSHIP
        else:
            return EvidenceType.WORK_EXPERIENCE

    def _calculate_proficiency_score(self, evidence_text: str, skill: str) -> int:
        """Calculate proficiency score based on context and depth"""
        base_score = 50
        text_lower = evidence_text.lower()
        
        # Boost for strong action verbs
        strong_verbs = ["optimized", "architected", "designed", "implemented", "scaled", "deployed"]
        for verb in strong_verbs:
            if verb in text_lower:
                base_score += 15
                
        # Boost for production/commercial context
        production_keywords = ["production", "commercial", "client", "customers", "live"]
        for keyword in production_keywords:
            if keyword in text_lower:
                base_score += 10
                
        # Boost for complexity indicators
        complexity_indicators = ["integration", "performance", "optimization", "scalability"]
        for indicator in complexity_indicators:
            if indicator in text_lower:
                base_score += 10
                
        # Penalty for beginner indicators
        beginner_keywords = ["coursework", "tutorial", "learning", "basic"]
        for keyword in beginner_keywords:
            if keyword in text_lower:
                base_score -= 20
                
        return min(100, max(20, base_score))

    def _extract_depth_indicators(self, evidence_text: str) -> List[str]:
        """Extract indicators of skill depth"""
        indicators = []
        text_lower = evidence_text.lower()
        
        all_indicators = []
        for level, keywords in self.depth_indicators.items():
            all_indicators.extend(keywords)
            
        for indicator in all_indicators:
            if indicator in text_lower:
                indicators.append(indicator)
                
        return indicators

    def _determine_skill_level(self, evidence_text: str, depth_indicators: List[str]) -> SkillLevel:
        """Determine skill level based on evidence and indicators"""
        text_lower = evidence_text.lower()
        
        # Count indicators for each level
        level_scores = {level: 0 for level in SkillLevel}
        
        for level, keywords in self.depth_indicators.items():
            for keyword in keywords:
                if keyword in text_lower:
                    level_scores[level] += 1
                    
        # Return the level with highest score
        max_level = max(level_scores, key=level_scores.get)
        return max_level if level_scores[max_level] > 0 else SkillLevel.INTERMEDIATE

    def _extract_soft_skills_with_evidence(self, cv_text: str) -> List[SoftSkillEvidence]:
        """Extract soft skills with evidence-based scoring"""
        soft_skills = []
        
        for skill_name, patterns in self.soft_skill_patterns.items():
            evidence_sentences = []
            
            for pattern in patterns:
                matches = re.finditer(pattern, cv_text, re.IGNORECASE)
                for match in matches:
                    # Get the full sentence containing the match
                    start = max(0, match.start() - 100)
                    end = min(len(cv_text), match.end() + 100)
                    context = cv_text[start:end]
                    
                    # Find sentence boundaries
                    sentences = re.split(r'[.!?]+', context)
                    for sentence in sentences:
                        if pattern.lower() in sentence.lower():
                            evidence_sentences.append(sentence.strip())
                            break
                            
            if evidence_sentences:
                # Calculate confidence based on number and quality of evidence
                confidence_score = min(90, len(evidence_sentences) * 30 + 30)
                
                soft_skills.append(SoftSkillEvidence(
                    skill_name=skill_name,
                    evidence_sentences=evidence_sentences[:3],  # Top 3 pieces of evidence
                    confidence_score=confidence_score,
                    supporting_context=' '.join(evidence_sentences[:2])
                ))
                
        return soft_skills

    def _extract_portfolio_links(self, cv_text: str) -> List[str]:
        """Extract portfolio and project links"""
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        links = re.findall(url_pattern, cv_text)
        
        # Filter for likely portfolio links
        portfolio_indicators = ['github', 'portfolio', 'project', 'demo', 'live', 'app']
        portfolio_links = []
        
        for link in links:
            if any(indicator in link.lower() for indicator in portfolio_indicators):
                portfolio_links.append(link)
                
        return portfolio_links

    def _extract_certifications(self, cv_text: str) -> List[Dict]:
        """Extract certifications with details"""
        certifications = []
        
        cert_patterns = [
            r'(Meta|Google|Amazon|Microsoft|Oracle|IBM)\s+([^.]+?)\s+(?:Certificate|Certification)',
            r'Certified\s+([^.]+?)(?:\s+by\s+([^.]+?))?',
            r'([^.]+?)\s+Certification(?:\s+by\s+([^.]+?))?'
        ]
        
        for pattern in cert_patterns:
            matches = re.finditer(pattern, cv_text, re.IGNORECASE)
            for match in matches:
                cert_name = match.group(1) if match.group(1) else "Unknown"
                issuer = match.group(2) if len(match.groups()) > 1 and match.group(2) else "Unknown"
                
                certifications.append({
                    "name": cert_name.strip(),
                    "issuer": issuer.strip() if issuer != "Unknown" else None,
                    "full_text": match.group(0)
                })
                
        return certifications

    def _analyze_career_progression(self, cv_text: str) -> List[Dict]:
        """Analyze career progression and growth"""
        # This would analyze job titles over time to identify career growth
        # For now, return basic structure
        return [
            {
                "insight": "Career progression analysis",
                "description": "Detailed career trajectory analysis would go here"
            }
        ]

    def _identify_strengths(self, technical_skills: List[SkillEvidence], soft_skills: List[SoftSkillEvidence]) -> List[str]:
        """Identify candidate's key strengths"""
        strengths = []
        
        # Technical strengths
        high_proficiency_skills = [skill for skill in technical_skills if skill.proficiency_score >= 80]
        if high_proficiency_skills:
            top_skill = max(high_proficiency_skills, key=lambda x: x.proficiency_score)
            strengths.append(f"Strong expertise in {top_skill.skill_name}")
            
        # Soft skill strengths
        high_confidence_soft = [skill for skill in soft_skills if skill.confidence_score >= 70]
        for skill in high_confidence_soft[:2]:  # Top 2
            strengths.append(f"Demonstrated {skill.skill_name.lower()}")
            
        return strengths

    def _generate_improvement_suggestions(self, cv_text: str, technical_skills: List[SkillEvidence]) -> List[str]:
        """Generate specific improvement suggestions"""
        suggestions = []
        
        # Check for missing context in skill descriptions
        basic_mentions = [skill for skill in technical_skills if skill.proficiency_score < 60]
        for skill in basic_mentions[:2]:
            suggestions.append(
                f"Enhance {skill.skill_name} description with specific project examples or achievements"
            )
            
        # Check for missing metrics
        if not re.search(r'\d+%|\d+x|improved|increased|reduced', cv_text, re.IGNORECASE):
            suggestions.append("Add quantifiable achievements and metrics to demonstrate impact")
            
        return suggestions

    def _generate_ai_insights(self, cv_text: str, technical_skills: List[SkillEvidence], soft_skills: List[SoftSkillEvidence]) -> str:
        """Generate AI-powered insights"""
        insights = []
        
        # Technical skill insights
        if technical_skills:
            top_skills = sorted(technical_skills, key=lambda x: x.proficiency_score, reverse=True)[:3]
            skill_names = [skill.skill_name for skill in top_skills]
            insights.append(f"Technical strengths center around {', '.join(skill_names)}")
            
        # Experience insights
        work_evidence = [skill for skill in technical_skills if skill.evidence_type == EvidenceType.WORK_EXPERIENCE]
        project_evidence = [skill for skill in technical_skills if skill.evidence_type == EvidenceType.PROJECT]
        
        if len(work_evidence) > len(project_evidence):
            insights.append("Strong commercial experience with practical application of skills")
        elif len(project_evidence) > len(work_evidence):
            insights.append("Project-focused experience showing initiative and learning drive")
            
        return ". ".join(insights) + "."

    def _analyze_job_fit(self, cv_text: str, job_description: str, technical_skills: List[SkillEvidence], 
                        soft_skills: List[SoftSkillEvidence], experience_years: float) -> JobFitAnalysis:
        """
        Comprehensive 6-section job fit analysis following HR hiring assessment format
        """
        
        # Extract job requirements from description
        job_requirements = self._extract_job_requirements(job_description)
        
        # Section 1: Overall Job Fit Summary
        overall_fit = self._generate_overall_fit_summary(cv_text, job_description, technical_skills, 
                                                       soft_skills, experience_years)
        
        # Section 2: Job Requirements Analysis (skill-by-skill comparison)
        requirement_breakdown = self._analyze_requirements_breakdown(technical_skills, job_requirements)
        
        # Section 3: Strengths for This Role
        strengths_for_role = self._identify_role_specific_strengths(technical_skills, soft_skills, job_requirements)
        
        # Section 4: Areas to Develop
        gaps_to_address = self._identify_skill_gaps_and_recommendations(technical_skills, job_requirements)
        
        # Calculate overall score
        overall_score = self._calculate_overall_match_score(requirement_breakdown)
        
        # Section 5: Hiring Recommendation
        hiring_decision, recommendation = self._generate_hiring_recommendation(overall_score, 
                                                                             requirement_breakdown, 
                                                                             strengths_for_role, 
                                                                             gaps_to_address)
        
        # Section 6: Interview Focus Areas
        interview_focus_areas = self._generate_interview_focus_areas(requirement_breakdown, gaps_to_address)
        
        return JobFitAnalysis(
            overall_fit=overall_fit,
            requirement_breakdown=requirement_breakdown,
            strengths_for_role=strengths_for_role,
            gaps_to_address=gaps_to_address,
            hiring_decision=hiring_decision,
            recommendation=recommendation,
            interview_focus_areas=interview_focus_areas,
            overall_score=overall_score
        )

    def match_with_job_description(self, cv_analysis: EnhancedCVAnalysis, job_description: str) -> Dict:
        """Advanced job matching with transferable skills consideration"""
        # Extract required skills from JD
        jd_skills = self._extract_jd_requirements(job_description)
        
        # Calculate match scores with transferability
        skill_matches = []
        for jd_skill in jd_skills:
            best_match = self._find_best_skill_match(jd_skill, cv_analysis.technical_skills)
            if best_match:
                skill_matches.append(best_match)
                
        # Calculate overall match score
        if jd_skills:
            match_percentage = (len(skill_matches) / len(jd_skills)) * 100
        else:
            match_percentage = 0
            
        return {
            "match_percentage": round(match_percentage, 1),
            "skill_matches": skill_matches,
            "missing_skills": [skill for skill in jd_skills if not self._find_best_skill_match(skill, cv_analysis.technical_skills)],
            "transferable_skills": [match for match in skill_matches if match.get("is_transferable", False)]
        }

    def _extract_jd_requirements(self, job_description: str) -> List[str]:
        """Extract required skills from job description"""
        # This would be more sophisticated in practice
        common_skills = ["react", "javascript", "python", "node.js", "typescript", "angular", "vue"]
        found_skills = []
        
        jd_lower = job_description.lower()
        for skill in common_skills:
            if skill in jd_lower:
                found_skills.append(skill)
                
        return found_skills

    def _find_best_skill_match(self, jd_skill: str, cv_skills: List[SkillEvidence]) -> Optional[Dict]:
        """Find best skill match considering transferability"""
        # Direct match
        for cv_skill in cv_skills:
            if cv_skill.skill_name.lower() == jd_skill.lower():
                return {
                    "jd_skill": jd_skill,
                    "cv_skill": cv_skill.skill_name,
                    "match_score": cv_skill.proficiency_score,
                    "is_transferable": False,
                    "evidence": cv_skill.evidence_text
                }
                
        # Transferable skills
        jd_skill_lower = jd_skill.lower()
        if jd_skill_lower in self.skill_transferability:
            for cv_skill in cv_skills:
                cv_skill_lower = cv_skill.skill_name.lower()
                if cv_skill_lower in self.skill_transferability[jd_skill_lower]:
                    transferability = self.skill_transferability[jd_skill_lower][cv_skill_lower]
                    match_score = (cv_skill.proficiency_score * transferability) // 100
                    
                    return {
                        "jd_skill": jd_skill,
                        "cv_skill": cv_skill.skill_name,
                        "match_score": match_score,
                        "is_transferable": True,
                        "transferability_score": transferability,
                        "evidence": cv_skill.evidence_text
                    }
                    
        return None

    # ==== 6-SECTION JOB FIT ANALYSIS HELPER METHODS ====
    
    def _extract_job_requirements(self, job_description: str) -> List[Dict]:
        """Extract required skills and proficiency levels from job description"""
        # Common tech skills with difficulty levels
        skills_to_find = [
            "react", "vue", "angular", "javascript", "typescript", "node.js", "python", 
            "django", "flask", "fastapi", "postgresql", "mongodb", "mysql", "aws", 
            "docker", "kubernetes", "git", "html", "css", "scss", "redux", "graphql",
            "rest api", "microservices", "ci/cd", "testing", "jest", "cypress"
        ]
        
        requirements = []
        jd_lower = job_description.lower()
        
        for skill in skills_to_find:
            if skill in jd_lower:
                # Determine required level based on context
                required_level = "Intermediate"
                context = self._extract_context_around_skill(jd_lower, skill)
                
                if any(word in context for word in ["senior", "expert", "advanced", "lead", "architect"]):
                    required_level = "Advanced"
                elif any(word in context for word in ["junior", "entry", "basic", "learn"]):
                    required_level = "Beginner"
                    
                requirements.append({
                    "skill": skill.title(),
                    "required_level": required_level,
                    "context": context[:100]
                })
                
        return requirements

    def _generate_overall_fit_summary(self, cv_text: str, job_description: str, technical_skills: List[SkillEvidence], 
                                    soft_skills: List[SoftSkillEvidence], experience_years: float) -> str:
        """Generate Section 1: Overall Job Fit - Professional hiring summary"""
        
        candidate_name = self._extract_candidate_name(cv_text)
        
        # 1. Candidate Profile Analysis
        profile_summary = f"{candidate_name} is a professional with {experience_years} years of experience in software development. "
        
        # Education/Certifications
        if "degree" in cv_text.lower() or "university" in cv_text.lower():
            profile_summary += "They hold relevant educational qualifications in their field. "
        
        # 2. Key Areas of Expertise
        top_skills = [skill.skill_name for skill in technical_skills[:5]]
        if top_skills:
            profile_summary += f"Their key technical expertise includes {', '.join(top_skills)}. "
        
        # 3. Career Trajectory & Growth Potential
        if experience_years >= 5:
            profile_summary += "The candidate demonstrates significant career progression and is well-suited for senior-level responsibilities. "
        elif experience_years >= 2:
            profile_summary += "Shows steady career growth and is ready for mid-level positions with potential for advancement. "
        else:
            profile_summary += "Early-career professional showing promise for rapid growth and development. "
        
        # 4. Suitable Role Types
        if experience_years >= 7:
            suitable_level = "Senior/Lead positions"
        elif experience_years >= 3:
            suitable_level = "Mid-level to Senior positions"
        else:
            suitable_level = "Junior to Mid-level positions"
            
        profile_summary += f"Most suitable for {suitable_level}. "
        
        # 5. Areas for Development
        if len(technical_skills) < 8:
            profile_summary += "Could benefit from expanding technical skill breadth. "
        
        # 6. Unique Value Proposition
        leadership_skills = [skill for skill in soft_skills if "leadership" in skill.skill_name.lower()]
        if leadership_skills:
            profile_summary += "Brings valuable leadership experience and mentoring capabilities. "
        
        if "github" in cv_text.lower() or "portfolio" in cv_text.lower():
            profile_summary += "Demonstrates commitment to professional development through portfolio work and open source contributions."
        
        return profile_summary

    def _analyze_requirements_breakdown(self, technical_skills: List[SkillEvidence], job_requirements: List[Dict]) -> List[Dict]:
        """Generate Section 2: Job Requirements Analysis - Skill-by-skill comparison table"""
        
        breakdown = []
        
        for req in job_requirements:
            req_skill = req["skill"].lower()
            
            # Find matching skill in CV
            matching_skill = None
            for skill in technical_skills:
                if req_skill in skill.skill_name.lower() or skill.skill_name.lower() in req_skill:
                    matching_skill = skill
                    break
            
            if matching_skill:
                # Determine candidate level based on evidence
                candidate_level = self._determine_candidate_level(matching_skill)
                score = self._calculate_skill_match_score(req["required_level"], candidate_level)
                notes = f"Evidence found: {matching_skill.evidence_text[:50]}..."
            else:
                candidate_level = "Not Found"
                score = 25
                notes = "No mention found in CV"
            
            breakdown.append({
                "skill": req["skill"],
                "required_level": req["required_level"],
                "candidate_level": candidate_level,
                "score": score,
                "notes": notes,
                "color": "green" if score >= 70 else "yellow" if score >= 40 else "red"
            })
            
        return breakdown

    def _identify_role_specific_strengths(self, technical_skills: List[SkillEvidence], 
                                        soft_skills: List[SoftSkillEvidence], job_requirements: List[Dict]) -> List[str]:
        """Generate Section 3: Strengths for This Role"""
        
        strengths = []
        
        # Technical strengths with evidence
        for skill in technical_skills[:6]:
            if skill.proficiency_score >= 60:
                strength = f"**{skill.skill_name}**: {skill.evidence_text[:80]}..."
                strengths.append(strength)
        
        # Soft skills strengths
        for soft_skill in soft_skills:
            if soft_skill.confidence_score >= 60:
                strength = f"**{soft_skill.skill_name}**: {soft_skill.supporting_context[:80]}..."
                strengths.append(strength)
        
        return strengths[:8]  # Limit to top 8 strengths

    def _identify_skill_gaps_and_recommendations(self, technical_skills: List[SkillEvidence], job_requirements: List[Dict]) -> List[str]:
        """Generate Section 4: Areas to Develop"""
        
        gaps = []
        skill_names = [skill.skill_name.lower() for skill in technical_skills]
        
        for req in job_requirements:
            req_skill = req["skill"].lower()
            if not any(req_skill in skill_name or skill_name in req_skill for skill_name in skill_names):
                recommendation = f"**Missing {req['skill']}**: Consider gaining experience through projects or certification"
                gaps.append(recommendation)
        
        # Add general recommendations
        if len(technical_skills) < 10:
            gaps.append("**Skill Breadth**: Expand technical skill set to include more modern frameworks and tools")
        
        return gaps[:6]  # Limit to top 6 gaps

    def _calculate_overall_match_score(self, requirement_breakdown: List[Dict]) -> int:
        """Calculate overall match percentage"""
        if not requirement_breakdown:
            return 50
            
        total_score = sum(req["score"] for req in requirement_breakdown)
        return min(100, int(total_score / len(requirement_breakdown)))

    def _generate_hiring_recommendation(self, overall_score: int, requirement_breakdown: List[Dict], 
                                      strengths: List[str], gaps: List[str]) -> Tuple[str, str]:
        """Generate Section 5: Hiring Recommendation"""
        
        if overall_score >= 80:
            decision = "Hire"
            recommendation = f"Strong candidate with {overall_score}% skill match. Technical competencies align well with role requirements. The candidate demonstrates proven experience and would be a valuable addition to the team. Minimal onboarding required."
        elif overall_score >= 60:
            decision = "Interview"
            recommendation = f"Promising candidate with {overall_score}% skill match. While there are some skill gaps, the candidate shows strong foundational skills and potential for growth. Recommend interview to assess cultural fit and learning ability."
        else:
            decision = "No Hire"
            recommendation = f"Limited match at {overall_score}%. Significant skill gaps would require extensive training and mentorship. Consider for more junior positions or after candidate gains additional experience."
            
        return decision, recommendation

    def _generate_interview_focus_areas(self, requirement_breakdown: List[Dict], gaps: List[str]) -> List[str]:
        """Generate Section 6: Interview Focus Areas"""
        
        focus_areas = []
        
        # Focus on skills that need clarification (moderate scores)
        for req in requirement_breakdown:
            if 40 <= req["score"] <= 75:
                focus_areas.append(f"🔹 Deep dive into {req['skill']} experience and practical applications")
        
        # Focus on high-scoring skills to validate
        high_score_skills = [req for req in requirement_breakdown if req["score"] >= 80]
        if high_score_skills:
            skill = high_score_skills[0]["skill"]
            focus_areas.append(f"🔹 Validate {skill} expertise through technical scenarios")
        
        # Focus on soft skills
        focus_areas.append("🔹 Assess problem-solving approach and analytical thinking")
        focus_areas.append("🔹 Evaluate communication skills and team collaboration style")
        
        # Focus on gaps
        if gaps:
            focus_areas.append("🔹 Discuss learning approach for new technologies and frameworks")
        
        return focus_areas[:6]  # Limit to 6 focus areas

    def _determine_candidate_level(self, skill: SkillEvidence) -> str:
        """Determine candidate skill level based on evidence"""
        if skill.proficiency_score >= 80:
            return "Expert"
        elif skill.proficiency_score >= 65:
            return "Advanced"
        elif skill.proficiency_score >= 45:
            return "Intermediate"
        else:
            return "Beginner"

    def _calculate_skill_match_score(self, required_level: str, candidate_level: str) -> int:
        """Calculate match score between required and candidate level"""
        level_scores = {
            "Expert": 100,
            "Advanced": 80, 
            "Intermediate": 60,
            "Beginner": 40,
            "Not Found": 25
        }
        
        required_score = level_scores.get(required_level, 60)
        candidate_score = level_scores.get(candidate_level, 25)
        
        # Calculate match percentage
        if candidate_score >= required_score:
            return min(100, candidate_score)
        else:
            return max(25, int((candidate_score / required_score) * 100))

    def _extract_context_around_skill(self, text: str, skill: str) -> str:
        """Extract context around a skill mention"""
        skill_index = text.find(skill)
        if skill_index == -1:
            return ""
        
        start = max(0, skill_index - 50)
        end = min(len(text), skill_index + len(skill) + 50)
        return text[start:end]
