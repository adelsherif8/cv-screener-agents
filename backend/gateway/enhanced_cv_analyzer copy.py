# Enhanced CV Analysis System
# This module implements advanced CV-Job matching with contextual reasoning

import re
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

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

class AdvancedCVAnalyzer:
    def __init__(self):
        # Skill transferability matrix (skill1 -> skill2: transferability_score)
        self.skill_transferability = {
            "react": {"vue": 70, "angular": 80, "svelte": 75, "javascript": 95},
            "vue": {"react": 70, "angular": 65, "svelte": 80, "javascript": 95},
            "angular": {"react": 80, "vue": 65, "typescript": 90, "javascript": 90},
            "javascript": {"typescript": 85, "react": 90, "vue": 90, "angular": 85, "node.js": 80},
            "typescript": {"javascript": 95, "angular": 95, "react": 85, "node.js": 85},
            "node.js": {"express": 90, "javascript": 85, "typescript": 80, "fastapi": 40},
            "express": {"node.js": 95, "fastapi": 50, "nest.js": 70},
            "mongodb": {"mongoose": 90, "postgresql": 60, "mysql": 65, "database": 80},
            "postgresql": {"mysql": 80, "mongodb": 50, "database": 90, "sql": 95},
            "mysql": {"postgresql": 85, "database": 90, "sql": 95, "mongodb": 45},
            "python": {"django": 85, "flask": 85, "fastapi": 80, "data analysis": 70},
            "django": {"python": 95, "flask": 75, "fastapi": 70, "web development": 80},
            "flask": {"python": 95, "django": 70, "fastapi": 80, "web development": 75},
            "fastapi": {"python": 90, "django": 65, "flask": 75, "rest api": 85}
        }
        
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
        """Perform comprehensive CV analysis with contextual reasoning"""
        
        # 1. Extract basic information
        candidate_name = self._extract_candidate_name(cv_text)
        primary_role = self._extract_primary_role(cv_text)
        experience_years = self._calculate_experience_years(cv_text)
        
        # 2. Advanced skill analysis with context
        technical_skills = self._analyze_technical_skills_with_context(cv_text)
        
        # 3. Soft skill evidence extraction
        soft_skills = self._extract_soft_skills_with_evidence(cv_text)
        
        # 4. Portfolio and certification analysis
        portfolio_links = self._extract_portfolio_links(cv_text)
        certifications = self._extract_certifications(cv_text)
        
        # 5. Career progression analysis
        career_progression = self._analyze_career_progression(cv_text)
        
        # 6. Generate improvement suggestions
        improvement_suggestions = self._generate_improvement_suggestions(cv_text, technical_skills)
        
        # 7. AI insights
        ai_insights = self._generate_ai_insights(cv_text, technical_skills, soft_skills)
        
        return EnhancedCVAnalysis(
            candidate_name=candidate_name,
            primary_role=primary_role,
            experience_years=experience_years,
            technical_skills=technical_skills,
            soft_skills=soft_skills,
            portfolio_links=portfolio_links,
            certifications=certifications,
            career_progression=career_progression,
            strengths=self._identify_strengths(technical_skills, soft_skills),
            improvement_suggestions=improvement_suggestions,
            ai_insights=ai_insights
        )

    def _extract_candidate_name(self, cv_text: str) -> str:
        """Extract candidate name with proper capitalization"""
        # Look for name patterns at the beginning of CV
        lines = cv_text.split('\n')[:5]  # Check first 5 lines
        
        for line in lines:
            line = line.strip()
            # Skip email, phone, address patterns
            if '@' in line or '+' in line or 'phone' in line.lower() or 'address' in line.lower():
                continue
                
            # Look for name-like patterns (allow lowercase first letter like "adel Atya")
            name_pattern = r'\b([a-zA-Z]+ [a-zA-Z]+(?:\s[a-zA-Z]+)?)\b'
            matches = re.findall(name_pattern, line)
            
            for match in matches:
                # Filter out common non-name phrases
                if not any(word.lower() in match.lower() for word in ['front', 'end', 'engineer', 'developer', 'links', 'profile']):
                    # Check if it looks like a name (2-3 words, reasonable length)
                    words = match.split()
                    if 2 <= len(words) <= 3 and all(2 <= len(word) <= 15 for word in words):
                        return match.title()  # Proper case
                
        # Fallback: look for patterns like "Name: John Doe" or start of text
        name_patterns = [
            r'name[:\s]+([a-zA-Z]+ [a-zA-Z]+)',
            r'^([a-zA-Z]+ [a-zA-Z]+)\s+(?:resume|cv|engineer|developer)',
            r'\b([a-zA-Z]+ [a-zA-Z]+)\s+Front[- ]?End',  # "Name Front End"
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
        
        # Enhanced date pattern matching
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
        base_score = 40  # Start lower for more realistic scoring
        text_lower = evidence_text.lower()
        
        # Strong boost for advanced action verbs (shows expertise)
        expert_verbs = ["optimized", "architected", "designed", "implemented", "scaled", "deployed", "enhanced"]
        for verb in expert_verbs:
            if verb in text_lower:
                base_score += 20
                
        # Medium boost for development verbs
        dev_verbs = ["developed", "built", "created", "integrated", "managed"]
        for verb in dev_verbs:
            if verb in text_lower:
                base_score += 15
                
        # Boost for production/commercial context
        production_keywords = ["production", "commercial", "client", "customers", "live", "freelancer", "company"]
        for keyword in production_keywords:
            if keyword in text_lower:
                base_score += 12
                
        # Boost for complexity indicators
        complexity_indicators = ["integration", "performance", "optimization", "scalability", "advanced", "responsive"]
        complexity_count = sum(1 for indicator in complexity_indicators if indicator in text_lower)
        base_score += complexity_count * 8
        
        # Boost for project mentions
        project_indicators = ["project", "platform", "system", "website", "application"]
        project_count = sum(1 for indicator in project_indicators if indicator in text_lower)
        base_score += project_count * 5
        
        # Boost for certification
        if "certified" in text_lower or "certification" in text_lower:
            base_score += 15
            
        # Moderate penalty for beginner indicators
        beginner_keywords = ["coursework", "tutorial", "learning", "basic", "studied"]
        for keyword in beginner_keywords:
            if keyword in text_lower:
                base_score -= 10
                
        # Special skill-specific scoring
        skill_lower = skill.lower()
        if skill_lower == "react" and ("next" in text_lower or "advanced" in text_lower):
            base_score += 15
        elif skill_lower == "javascript" and ("typescript" in text_lower or "es6" in text_lower):
            base_score += 10
            
        return min(95, max(25, base_score))  # Keep realistic range

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
