"""
OpenAI GPT Integration Service
Provides real AI capabilities for job analysis, generation, and suggestions
"""

import os
import asyncio
import logging
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
import openai
from openai import OpenAI
import json

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class AIService:
    """OpenAI GPT integration service"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.org_id = os.getenv("OPENAI_ORG_ID")
        self.enabled = os.getenv("AI_ENABLED", "true").lower() == "true"
        self.fallback_enabled = os.getenv("AI_FALLBACK_ENABLED", "true").lower() == "true"
        
        if self.enabled and self.api_key and self.api_key != "your_openai_api_key_here":
            try:
                self.client = OpenAI(
                    api_key=self.api_key,
                    organization=self.org_id if self.org_id else None
                )
                # Test the connection
                self._test_connection()
                logger.info(f"✅ OpenAI AI Service initialized with model: {self.model}")
            except Exception as e:
                logger.error(f"❌ Failed to initialize OpenAI client: {str(e)}")
                self.enabled = False
                self.client = None
        else:
            self.enabled = False
            self.client = None
            if not self.api_key or self.api_key == "your_openai_api_key_here":
                logger.warning("🔑 OpenAI API key not configured. Using fallback AI.")
            else:
                logger.info("🔄 AI disabled in configuration. Using fallback AI.")
    
    def _test_connection(self):
        """Test OpenAI API connection"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Test connection - respond with 'OK'"}],
                max_tokens=5
            )
            logger.info("✅ OpenAI connection test successful")
        except Exception as e:
            logger.error(f"❌ OpenAI connection test failed: {str(e)}")
            raise
    
    async def generate_job_summary(self, job_data: Dict, style: str = "standard") -> str:
        """Generate AI-powered job summary"""
        if not self.enabled:
            return self._fallback_generate_summary(job_data, style)
        
        try:
            title = job_data.get('title', 'Untitled Position')
            description = job_data.get('description', '')
            requirements = job_data.get('requirements', [])
            seniority = job_data.get('seniority', '')
            
            # Create context-aware prompt
            prompt = self._build_summary_prompt(title, description, requirements, seniority, style)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert HR professional and content writer specializing in creating compelling job descriptions and summaries."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            summary = response.choices[0].message.content.strip()
            logger.info(f"✅ Generated AI summary for: {title}")
            return summary
            
        except Exception as e:
            logger.error(f"❌ AI summary generation failed: {str(e)}")
            if self.fallback_enabled:
                return self._fallback_generate_summary(job_data, style)
            else:
                raise
    
    async def analyze_job_requirements(self, title: str, description: str) -> Dict:
        """AI-powered job requirements analysis"""
        if not self.enabled:
            return self._fallback_analyze_requirements(title, description)
        
        try:
            prompt = f"""
            Analyze this job posting and extract structured information:
            
            Title: {title}
            Description: {description}
            
            Please provide a JSON response with:
            {{
                "core_skills": [list of essential technical skills],
                "soft_skills": [list of important soft skills], 
                "experience_level": "entry/mid/senior/lead",
                "estimated_salary_range": {{"min": number, "max": number}},
                "industry": "primary industry category",
                "remote_friendly": boolean,
                "key_responsibilities": [list of main responsibilities],
                "growth_opportunities": [list of career growth aspects],
                "company_benefits": [list of mentioned benefits],
                "urgency_level": "low/medium/high",
                "role_type": "individual_contributor/team_lead/management"
            }}
            
            Be thorough but concise. Use null for unclear information.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert HR analyst. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.3
            )
            
            analysis_text = response.choices[0].message.content.strip()
            # Parse JSON response
            analysis = json.loads(analysis_text)
            
            logger.info(f"✅ AI analysis completed for: {title}")
            return analysis
            
        except Exception as e:
            logger.error(f"❌ AI analysis failed: {str(e)}")
            if self.fallback_enabled:
                return self._fallback_analyze_requirements(title, description)
            else:
                raise
    
    async def generate_smart_suggestions(self, context: str, suggestion_type: str = "skills") -> List[str]:
        """Generate smart suggestions for job creation"""
        if not self.enabled:
            return self._fallback_generate_suggestions(context, suggestion_type)
        
        try:
            if suggestion_type == "skills":
                prompt = f"""
                Based on this job context: "{context}"
                
                Suggest 8-12 relevant technical skills that would be valuable for this role.
                Consider both essential and nice-to-have skills.
                Return as a simple JSON array of strings.
                
                Example: ["React", "TypeScript", "Node.js", "AWS", "Docker"]
                """
            elif suggestion_type == "questions":
                prompt = f"""
                Based on this job context: "{context}"
                
                Suggest 5-7 effective screening questions for interviewing candidates.
                Include both technical and behavioral questions.
                Return as a JSON array of strings.
                """
            else:
                prompt = f"""
                Based on this job context: "{context}"
                
                Suggest relevant content for {suggestion_type}.
                Return as a JSON array of strings.
                """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert HR consultant. Always respond with valid JSON arrays only."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.6
            )
            
            suggestions_text = response.choices[0].message.content.strip()
            suggestions = json.loads(suggestions_text)
            
            logger.info(f"✅ Generated {len(suggestions)} AI suggestions for {suggestion_type}")
            return suggestions
            
        except Exception as e:
            logger.error(f"❌ AI suggestions failed: {str(e)}")
            if self.fallback_enabled:
                return self._fallback_generate_suggestions(context, suggestion_type)
            else:
                raise
    
    def _build_summary_prompt(self, title: str, description: str, requirements: List, seniority: str, style: str) -> str:
        """Build context-aware prompt for job summary generation"""
        req_text = ", ".join([req if isinstance(req, str) else req.get('skill', '') for req in requirements])
        
        if style == "ats":
            return f"""
            Create an ATS-optimized job summary for this position:
            
            Title: {title}
            Level: {seniority}
            Description: {description}
            Key Skills: {req_text}
            
            Requirements:
            - Use relevant keywords for ATS scanning
            - Include skill variations and synonyms
            - Structure for easy parsing
            - 200-300 words
            - Professional tone
            """
        elif style == "short":
            return f"""
            Create a concise job summary for this position:
            
            Title: {title}
            Level: {seniority}
            Description: {description}
            Key Skills: {req_text}
            
            Requirements:
            - 100-150 words maximum
            - Highlight top 3-4 key points
            - Engaging and direct
            - Focus on value proposition
            """
        else:  # standard
            return f"""
            Create a comprehensive job summary for this position:
            
            Title: {title}
            Level: {seniority}
            Description: {description}
            Key Skills: {req_text}
            
            Requirements:
            - Professional and engaging tone
            - Clear role overview
            - Highlight key responsibilities
            - Mention growth opportunities
            - Include team/company culture fit
            - 300-400 words
            """
    
    def _fallback_generate_summary(self, job_data: Dict, style: str) -> str:
        """Fallback summary generation using rule-based approach"""
        from .main import generate_summary_ai as fallback_ai
        logger.info("🔄 Using fallback AI for summary generation")
        return fallback_ai(job_data, style)
    
    def _fallback_analyze_requirements(self, title: str, description: str) -> Dict:
        """Fallback requirements analysis using rule-based approach"""
        from .main import analyze_requirements_ai as fallback_analyze
        logger.info("🔄 Using fallback AI for requirements analysis")
        return fallback_analyze(title, description)
    
    def _fallback_generate_suggestions(self, context: str, suggestion_type: str) -> List[str]:
        """Fallback suggestions using rule-based approach"""
        logger.info("🔄 Using fallback AI for suggestions")
        # Simple fallback suggestions
        if suggestion_type == "skills":
            return ["Communication", "Problem Solving", "Teamwork", "Attention to Detail"]
        elif suggestion_type == "questions":
            return [
                "Tell me about your experience with this technology stack",
                "How do you handle challenging technical problems?",
                "Describe a project you're particularly proud of",
                "How do you stay updated with industry trends?"
            ]
        else:
            return ["Please configure OpenAI API for advanced suggestions"]

# Global AI service instance
ai_service = AIService()

# Convenience functions for easy import
async def generate_ai_summary(job_data: Dict, style: str = "standard") -> str:
    """Generate AI-powered job summary"""
    return await ai_service.generate_job_summary(job_data, style)

async def analyze_ai_requirements(title: str, description: str) -> Dict:
    """AI-powered job requirements analysis"""
    return await ai_service.analyze_job_requirements(title, description)

async def generate_ai_suggestions(context: str, suggestion_type: str = "skills") -> List[str]:
    """Generate smart AI suggestions"""
    return await ai_service.generate_smart_suggestions(context, suggestion_type)

def is_ai_enabled() -> bool:
    """Check if AI services are enabled and working"""
    return ai_service.enabled

def get_ai_status() -> Dict:
    """Get detailed AI service status"""
    return {
        "enabled": ai_service.enabled,
        "model": ai_service.model,
        "fallback_enabled": ai_service.fallback_enabled,
        "api_key_configured": bool(ai_service.api_key and ai_service.api_key != "your_openai_api_key_here")
    }
