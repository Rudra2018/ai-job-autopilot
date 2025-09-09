#!/usr/bin/env python3
"""
Multi-AI Service Integration
Integrates OpenAI, Anthropic (Claude), and Google Gemini for enhanced AI capabilities
"""

import os
import logging
import json
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import AI service clients
try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

try:
    from anthropic import Anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

class AIProvider(Enum):
    """Available AI service providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"

@dataclass
class AIResponse:
    """Standardized AI response"""
    content: str
    provider: AIProvider
    model: str
    tokens_used: Optional[int] = None
    cost_estimate: Optional[float] = None
    processing_time: Optional[float] = None
    success: bool = True
    error: Optional[str] = None

class MultiAIService:
    """Multi-AI service integration for enhanced resume processing"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize available services
        self.openai_client = None
        self.anthropic_client = None
        self.gemini_client = None
        
        self._initialize_services()
        
        # Service priority for fallbacks
        self.service_priority = [AIProvider.OPENAI, AIProvider.ANTHROPIC, AIProvider.GEMINI]
        
    def _initialize_services(self):
        """Initialize available AI services"""
        
        # Initialize OpenAI
        if HAS_OPENAI and os.getenv("OPENAI_API_KEY"):
            try:
                openai.api_key = os.getenv("OPENAI_API_KEY")
                self.openai_client = openai
                self.logger.info("OpenAI service initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize OpenAI: {e}")
        
        # Initialize Anthropic (Claude)
        if HAS_ANTHROPIC and os.getenv("ANTHROPIC_API_KEY"):
            try:
                self.anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
                self.logger.info("Anthropic (Claude) service initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize Anthropic: {e}")
        
        # Initialize Google Gemini
        if HAS_GEMINI and os.getenv("GEMINI_API_KEY"):
            try:
                genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
                self.gemini_client = genai
                self.logger.info("Google Gemini service initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize Gemini: {e}")
    
    def get_available_services(self) -> List[AIProvider]:
        """Get list of available AI services"""
        available = []
        if self.openai_client:
            available.append(AIProvider.OPENAI)
        if self.anthropic_client:
            available.append(AIProvider.ANTHROPIC)
        if self.gemini_client:
            available.append(AIProvider.GEMINI)
        return available
    
    async def enhance_resume_summary(
        self, 
        resume_data: Dict, 
        target_job: Optional[str] = None,
        preferred_provider: Optional[AIProvider] = None
    ) -> AIResponse:
        """Generate enhanced resume summary using AI"""
        
        prompt = self._create_summary_enhancement_prompt(resume_data, target_job)
        
        return await self._call_ai_service(
            prompt=prompt,
            system_message="You are a professional resume writer and career coach. Create compelling, ATS-friendly resume summaries.",
            preferred_provider=preferred_provider,
            task="resume_summary_enhancement"
        )
    
    async def analyze_resume_quality(
        self, 
        resume_data: Dict,
        preferred_provider: Optional[AIProvider] = None
    ) -> AIResponse:
        """Analyze resume quality and provide recommendations"""
        
        prompt = f"""
        Analyze this resume and provide detailed feedback:
        
        Resume Data:
        {json.dumps(resume_data, indent=2)}
        
        Please provide:
        1. Overall quality score (1-10)
        2. Strengths (3-5 points)
        3. Areas for improvement (3-5 points) 
        4. ATS compatibility assessment
        5. Specific recommendations for enhancement
        6. Missing sections or information
        7. Industry-specific suggestions
        
        Format your response as structured JSON with clear sections.
        """
        
        return await self._call_ai_service(
            prompt=prompt,
            system_message="You are an expert resume reviewer and ATS optimization specialist.",
            preferred_provider=preferred_provider,
            task="resume_quality_analysis"
        )
    
    async def generate_cover_letter(
        self,
        resume_data: Dict,
        job_description: str,
        company_name: str,
        position_title: str,
        preferred_provider: Optional[AIProvider] = None
    ) -> AIResponse:
        """Generate a personalized cover letter"""
        
        prompt = f"""
        Create a compelling cover letter based on this information:
        
        Resume Summary:
        Name: {resume_data.get('contact_info', {}).get('name', 'Candidate')}
        Experience: {len(resume_data.get('work_experience', []))} roles
        Key Skills: {', '.join(resume_data.get('skills', [])[:10])}
        Latest Role: {resume_data.get('work_experience', [{}])[0].get('position', 'N/A') if resume_data.get('work_experience') else 'N/A'}
        
        Target Position: {position_title}
        Company: {company_name}
        
        Job Description:
        {job_description}
        
        Create a professional cover letter that:
        1. Shows enthusiasm for the specific role and company
        2. Highlights relevant experience and achievements
        3. Addresses key requirements from the job description
        4. Is concise (under 300 words)
        5. Has a professional but engaging tone
        6. Includes a strong opening and closing
        """
        
        return await self._call_ai_service(
            prompt=prompt,
            system_message="You are a professional career coach specializing in creating compelling cover letters.",
            preferred_provider=preferred_provider,
            task="cover_letter_generation"
        )
    
    async def match_job_compatibility(
        self,
        resume_data: Dict,
        job_description: str,
        preferred_provider: Optional[AIProvider] = None
    ) -> AIResponse:
        """Analyze job compatibility with detailed matching"""
        
        prompt = f"""
        Analyze the compatibility between this resume and job description:
        
        Resume Data:
        Skills: {resume_data.get('skills', [])}
        Experience: {resume_data.get('work_experience', [])}
        Education: {resume_data.get('education', [])}
        
        Job Description:
        {job_description}
        
        Provide a detailed analysis including:
        1. Overall compatibility score (0-100%)
        2. Matching skills and technologies
        3. Missing skills that are required
        4. Experience level alignment
        5. Education requirement match
        6. Transferable skills identification
        7. Specific recommendations to improve match
        8. Application strategy (should apply / needs preparation / not suitable)
        
        Return results as structured JSON.
        """
        
        return await self._call_ai_service(
            prompt=prompt,
            system_message="You are an expert talent acquisition specialist and job matching analyst.",
            preferred_provider=preferred_provider,
            task="job_compatibility_analysis"
        )
    
    async def optimize_for_ats(
        self,
        resume_data: Dict,
        job_keywords: List[str],
        preferred_provider: Optional[AIProvider] = None
    ) -> AIResponse:
        """Optimize resume for ATS systems"""
        
        prompt = f"""
        Optimize this resume for Applicant Tracking Systems (ATS):
        
        Current Resume Data:
        {json.dumps(resume_data, indent=2)}
        
        Target Keywords: {', '.join(job_keywords)}
        
        Provide ATS optimization recommendations:
        1. Keyword integration suggestions
        2. Section formatting improvements
        3. Skills section optimization
        4. Experience description enhancements
        5. ATS-friendly formatting tips
        6. Common ATS pitfalls to avoid
        7. Industry-specific keyword suggestions
        8. Quantifiable achievement recommendations
        
        Focus on maintaining authenticity while maximizing ATS compatibility.
        """
        
        return await self._call_ai_service(
            prompt=prompt,
            system_message="You are an ATS optimization expert and technical recruiter.",
            preferred_provider=preferred_provider,
            task="ats_optimization"
        )
    
    async def generate_linkedin_content(
        self,
        resume_data: Dict,
        content_type: str = "summary",
        preferred_provider: Optional[AIProvider] = None
    ) -> AIResponse:
        """Generate LinkedIn profile content"""
        
        if content_type == "summary":
            prompt = f"""
            Create a compelling LinkedIn summary based on this resume:
            
            {json.dumps(resume_data, indent=2)}
            
            The LinkedIn summary should:
            1. Be engaging and professional (2-3 paragraphs)
            2. Include relevant keywords for searchability
            3. Show personality and passion
            4. Highlight key achievements and skills
            5. Include a call-to-action
            6. Be written in first person
            7. Appeal to both recruiters and networking contacts
            """
        else:
            prompt = f"""
            Generate LinkedIn content for: {content_type}
            Based on resume data: {json.dumps(resume_data, indent=2)}
            """
        
        return await self._call_ai_service(
            prompt=prompt,
            system_message="You are a LinkedIn profile optimization expert and personal branding specialist.",
            preferred_provider=preferred_provider,
            task="linkedin_content_generation"
        )
    
    async def _call_ai_service(
        self,
        prompt: str,
        system_message: str,
        preferred_provider: Optional[AIProvider] = None,
        task: str = "general"
    ) -> AIResponse:
        """Call AI service with fallback support"""
        
        import time
        start_time = time.time()
        
        # Determine service order
        services_to_try = []
        if preferred_provider and preferred_provider in self.get_available_services():
            services_to_try.append(preferred_provider)
        
        # Add other available services as fallbacks
        for provider in self.service_priority:
            if provider not in services_to_try and provider in self.get_available_services():
                services_to_try.append(provider)
        
        # Try each service
        for provider in services_to_try:
            try:
                response = await self._call_specific_service(provider, prompt, system_message)
                response.processing_time = time.time() - start_time
                return response
                
            except Exception as e:
                self.logger.warning(f"{provider.value} failed for task {task}: {e}")
                continue
        
        # All services failed
        return AIResponse(
            content="",
            provider=AIProvider.OPENAI,  # Default
            model="unavailable",
            success=False,
            error="All AI services unavailable or failed",
            processing_time=time.time() - start_time
        )
    
    async def _call_specific_service(
        self, 
        provider: AIProvider, 
        prompt: str, 
        system_message: str
    ) -> AIResponse:
        """Call specific AI service"""
        
        if provider == AIProvider.OPENAI and self.openai_client:
            return await self._call_openai(prompt, system_message)
        elif provider == AIProvider.ANTHROPIC and self.anthropic_client:
            return await self._call_anthropic(prompt, system_message)
        elif provider == AIProvider.GEMINI and self.gemini_client:
            return await self._call_gemini(prompt, system_message)
        else:
            raise ValueError(f"Service {provider.value} not available")
    
    async def _call_openai(self, prompt: str, system_message: str) -> AIResponse:
        """Call OpenAI GPT"""
        response = await self.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        return AIResponse(
            content=response.choices[0].message.content,
            provider=AIProvider.OPENAI,
            model="gpt-3.5-turbo",
            tokens_used=response.usage.total_tokens,
            cost_estimate=response.usage.total_tokens * 0.002 / 1000  # Rough estimate
        )
    
    async def _call_anthropic(self, prompt: str, system_message: str) -> AIResponse:
        """Call Anthropic Claude"""
        message = await self.anthropic_client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1000,
            system=system_message,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return AIResponse(
            content=message.content[0].text,
            provider=AIProvider.ANTHROPIC,
            model="claude-3-sonnet",
            tokens_used=message.usage.input_tokens + message.usage.output_tokens if hasattr(message, 'usage') else None
        )
    
    async def _call_gemini(self, prompt: str, system_message: str) -> AIResponse:
        """Call Google Gemini"""
        model = self.gemini_client.GenerativeModel('gemini-1.5-flash')  # Use available model
        
        full_prompt = f"{system_message}\n\nUser Request:\n{prompt}"
        
        response = await model.generate_content_async(full_prompt)
        
        return AIResponse(
            content=response.text,
            provider=AIProvider.GEMINI,
            model="gemini-pro"
        )
    
    def _create_summary_enhancement_prompt(self, resume_data: Dict, target_job: Optional[str] = None) -> str:
        """Create prompt for summary enhancement"""
        
        context = f"""
        Enhance the professional summary for this resume:
        
        Current Summary: {resume_data.get('summary', 'None provided')}
        Experience Level: {len(resume_data.get('work_experience', []))} roles
        Key Skills: {', '.join(resume_data.get('skills', [])[:10])}
        Industry: {resume_data.get('work_experience', [{}])[0].get('company', 'N/A') if resume_data.get('work_experience') else 'Technology'}
        Education: {resume_data.get('education', [{}])[0].get('degree', 'N/A') if resume_data.get('education') else 'N/A'}
        """
        
        if target_job:
            context += f"\nTarget Role: {target_job}"
        
        context += """
        
        Create a compelling professional summary that:
        1. Is 2-3 sentences long
        2. Highlights key strengths and experience
        3. Includes relevant keywords for ATS
        4. Shows value proposition to employers
        5. Is engaging but professional
        6. Quantifies experience where possible
        
        Professional Summary:
        """
        
        return context

# Convenience functions for direct usage
async def enhance_resume_with_ai(
    resume_data: Dict,
    task: str = "summary",
    target_job: Optional[str] = None,
    job_description: Optional[str] = None
) -> AIResponse:
    """Enhanced resume processing with multi-AI support"""
    
    ai_service = MultiAIService()
    
    if task == "summary":
        return await ai_service.enhance_resume_summary(resume_data, target_job)
    elif task == "analysis":
        return await ai_service.analyze_resume_quality(resume_data)
    elif task == "job_match" and job_description:
        return await ai_service.match_job_compatibility(resume_data, job_description)
    elif task == "ats_optimization":
        keywords = job_description.split() if job_description else []
        return await ai_service.optimize_for_ats(resume_data, keywords)
    elif task == "cover_letter" and job_description:
        return await ai_service.generate_cover_letter(
            resume_data, job_description, "Company", "Position"
        )
    else:
        raise ValueError(f"Unknown task: {task}")

if __name__ == "__main__":
    # Test the multi-AI service
    import asyncio
    
    async def test_multi_ai():
        ai_service = MultiAIService()
        
        print("Available AI services:", [s.value for s in ai_service.get_available_services()])
        
        # Test with sample data
        sample_resume = {
            "contact_info": {"name": "Test User"},
            "skills": ["Python", "JavaScript", "React"],
            "work_experience": [{"position": "Developer", "company": "TechCorp"}],
            "summary": "Experienced developer"
        }
        
        # Test summary enhancement
        response = await ai_service.enhance_resume_summary(sample_resume)
        
        if response.success:
            print(f"\n✅ AI Enhancement Success ({response.provider.value}):")
            print(response.content[:200] + "...")
        else:
            print(f"❌ AI Enhancement Failed: {response.error}")
    
    asyncio.run(test_multi_ai())