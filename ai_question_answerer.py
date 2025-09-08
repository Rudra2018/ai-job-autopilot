#!/usr/bin/env python3
"""
🤖 AI Job Autopilot - Intelligent Question Answering System
Dynamically answers job application questions using multiple AI providers
"""

import os
import json
import hashlib
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
import openai
import anthropic
import google.generativeai as genai
from dataclasses import dataclass, asdict
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class QuestionAnswer:
    question: str
    answer: str
    job_title: str = ""
    company: str = ""
    timestamp: str = ""
    ai_provider: str = ""
    confidence: float = 0.0

class AIQuestionAnswerer:
    def __init__(self, user_profile_path: str = "config/user_profile.yaml"):
        self.user_profile_path = user_profile_path
        self.answers_cache_path = Path("data/question_answers_cache.json")
        self.answers_cache_path.parent.mkdir(exist_ok=True)
        
        # Load user profile and cache
        self.user_profile = self._load_user_profile()
        self.answers_cache = self._load_answers_cache()
        
        # Initialize AI clients
        self.openai_client = None
        self.anthropic_client = None
        self.gemini_client = None
        
        self._initialize_ai_clients()
        
        # Question patterns for categorization
        self.question_categories = {
            "experience": ["experience", "years", "worked", "background", "previous"],
            "motivation": ["why", "interested", "motivation", "passionate", "excited"],
            "skills": ["skills", "expertise", "proficient", "familiar", "knowledge"],
            "availability": ["available", "start", "notice", "relocate", "travel"],
            "salary": ["salary", "compensation", "pay", "rate", "budget"],
            "education": ["degree", "education", "university", "certification", "graduate"],
            "location": ["location", "remote", "office", "hybrid", "relocate"],
            "company": ["company", "organization", "team", "culture", "values"]
        }
    
    def _load_user_profile(self) -> Dict:
        """Load user profile from YAML file"""
        try:
            import yaml
            if os.path.exists(self.user_profile_path):
                with open(self.user_profile_path, 'r') as f:
                    return yaml.safe_load(f)
            else:
                logger.warning(f"User profile not found at {self.user_profile_path}")
                return self._create_default_profile()
        except Exception as e:
            logger.error(f"Error loading user profile: {e}")
            return self._create_default_profile()
    
    def _create_default_profile(self) -> Dict:
        """Create a default user profile structure"""
        return {
            "name": "Job Applicant",
            "email": "applicant@email.com",
            "phone": "+1-234-567-8900",
            "experience_years": 5,
            "current_role": "Software Engineer",
            "skills": ["Python", "JavaScript", "React", "Node.js"],
            "availability": {
                "notice_period": "2 weeks",
                "start_date": "Flexible",
                "remote_preference": "Hybrid"
            },
            "education": {
                "degree": "Bachelor's in Computer Science",
                "university": "State University"
            },
            "preferences": {
                "preferred_salary_range": "$80,000-$120,000",
                "willing_to_relocate": False,
                "travel_percentage": "< 25%"
            }
        }
    
    def _load_answers_cache(self) -> Dict:
        """Load previously answered questions from cache"""
        try:
            if self.answers_cache_path.exists():
                with open(self.answers_cache_path, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Error loading answers cache: {e}")
            return {}
    
    def _save_answers_cache(self):
        """Save answers cache to file"""
        try:
            with open(self.answers_cache_path, 'w') as f:
                json.dump(self.answers_cache, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving answers cache: {e}")
    
    def _initialize_ai_clients(self):
        """Initialize AI clients for multiple providers"""
        try:
            # OpenAI
            openai_key = os.getenv("OPENAI_API_KEY")
            if openai_key:
                self.openai_client = openai.OpenAI(api_key=openai_key)
                logger.info("OpenAI client initialized")
        
            # Anthropic
            anthropic_key = os.getenv("ANTHROPIC_API_KEY")
            if anthropic_key:
                self.anthropic_client = anthropic.Anthropic(api_key=anthropic_key)
                logger.info("Anthropic client initialized")
            
            # Google Gemini
            google_key = os.getenv("GOOGLE_API_KEY")
            if google_key:
                genai.configure(api_key=google_key)
                self.gemini_client = genai.GenerativeModel('gemini-pro')
                logger.info("Google Gemini client initialized")
                
        except Exception as e:
            logger.error(f"Error initializing AI clients: {e}")
    
    def _get_question_hash(self, question: str, job_context: Dict = None) -> str:
        """Generate hash for question to check cache"""
        content = question.lower().strip()
        if job_context:
            content += f"_{job_context.get('title', '')}_{job_context.get('company', '')}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _categorize_question(self, question: str) -> str:
        """Categorize question based on keywords"""
        question_lower = question.lower()
        for category, keywords in self.question_categories.items():
            if any(keyword in question_lower for keyword in keywords):
                return category
        return "general"
    
    def _check_cache(self, question_hash: str) -> Optional[QuestionAnswer]:
        """Check if question was answered before"""
        if question_hash in self.answers_cache:
            cached_data = self.answers_cache[question_hash]
            return QuestionAnswer(**cached_data)
        return None
    
    def _cache_answer(self, question_hash: str, qa: QuestionAnswer):
        """Cache the question-answer pair"""
        self.answers_cache[question_hash] = asdict(qa)
        self._save_answers_cache()
    
    def _build_context_prompt(self, question: str, job_context: Dict = None, category: str = "general") -> str:
        """Build context-aware prompt for AI"""
        
        # Base context from user profile
        context = f"""
You are helping a job applicant answer application questions. Here is their profile:

Name: {self.user_profile.get('name', 'N/A')}
Current Role: {self.user_profile.get('current_role', 'N/A')}
Experience: {self.user_profile.get('experience_years', 'N/A')} years
Skills: {', '.join(self.user_profile.get('skills', []))}
Education: {self.user_profile.get('education', {}).get('degree', 'N/A')} from {self.user_profile.get('education', {}).get('university', 'N/A')}
"""
        
        # Add job-specific context if available
        if job_context:
            context += f"""
Job Details:
- Title: {job_context.get('title', 'N/A')}
- Company: {job_context.get('company', 'N/A')}
- Description: {job_context.get('description', 'N/A')[:500]}...
"""
        
        # Category-specific instructions
        category_instructions = {
            "experience": "Focus on relevant work experience and achievements. Be specific but concise.",
            "motivation": "Show genuine interest and alignment with the role/company. Be enthusiastic but professional.",
            "skills": "Highlight relevant technical and soft skills with brief examples.",
            "availability": f"Use preferences: {self.user_profile.get('availability', {})}",
            "salary": f"Reference range: {self.user_profile.get('preferences', {}).get('preferred_salary_range', 'Competitive')}",
            "education": "Highlight relevant educational background and certifications.",
            "location": f"Remote preference: {self.user_profile.get('availability', {}).get('remote_preference', 'Flexible')}",
            "company": "Research the company and show knowledge of their values/mission."
        }
        
        instruction = category_instructions.get(category, "Provide a professional, relevant answer.")
        
        prompt = f"""
{context}

Category: {category}
Instruction: {instruction}

Question: "{question}"

Provide a concise, professional answer (1-3 sentences) that:
1. Directly addresses the question
2. Uses information from the profile when relevant
3. Sounds natural and authentic
4. Is appropriate for a job application

Answer:"""
        
        return prompt
    
    def _query_openai(self, prompt: str) -> Optional[str]:
        """Query OpenAI GPT"""
        try:
            if not self.openai_client:
                return None
                
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional job application assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI query error: {e}")
            return None
    
    def _query_anthropic(self, prompt: str) -> Optional[str]:
        """Query Anthropic Claude"""
        try:
            if not self.anthropic_client:
                return None
                
            response = self.anthropic_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=150,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text.strip()
        except Exception as e:
            logger.error(f"Anthropic query error: {e}")
            return None
    
    def _query_gemini(self, prompt: str) -> Optional[str]:
        """Query Google Gemini"""
        try:
            if not self.gemini_client:
                return None
                
            response = self.gemini_client.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=150,
                    temperature=0.3,
                )
            )
            return response.text.strip()
        except Exception as e:
            logger.error(f"Gemini query error: {e}")
            return None
    
    def _get_fallback_answer(self, question: str, category: str) -> str:
        """Generate fallback answer when AI fails"""
        fallback_answers = {
            "experience": f"I have {self.user_profile.get('experience_years', 'several')} years of experience in {self.user_profile.get('current_role', 'my field')}, with expertise in {', '.join(self.user_profile.get('skills', [])[:3])}.",
            "motivation": "I'm excited about this opportunity because it aligns with my career goals and allows me to contribute my skills while continuing to grow professionally.",
            "skills": f"My key skills include {', '.join(self.user_profile.get('skills', [])[:5])}, which I've developed through hands-on experience in my current role.",
            "availability": f"I'm available to start with {self.user_profile.get('availability', {}).get('notice_period', '2 weeks')} notice and am flexible with start dates.",
            "salary": "I'm looking for competitive compensation commensurate with my experience and the market rate for this role.",
            "education": f"I hold a {self.user_profile.get('education', {}).get('degree', 'relevant degree')} which provided me with a strong foundation in my field.",
            "location": f"I prefer {self.user_profile.get('availability', {}).get('remote_preference', 'flexible')} work arrangements and am open to discussing location requirements.",
            "company": "I'm impressed by your company's reputation and would love to contribute to your team's continued success."
        }
        
        return fallback_answers.get(category, "Thank you for this question. I believe my background and experience make me a strong candidate for this position.")
    
    def answer_question(self, question: str, job_context: Dict = None) -> QuestionAnswer:
        """
        Main method to answer application questions intelligently
        
        Args:
            question: The application question to answer
            job_context: Optional job details (title, company, description)
            
        Returns:
            QuestionAnswer object with the generated answer
        """
        
        # Check cache first
        question_hash = self._get_question_hash(question, job_context)
        cached_answer = self._check_cache(question_hash)
        
        if cached_answer:
            logger.info(f"Using cached answer for: {question[:50]}...")
            return cached_answer
        
        # Categorize question
        category = self._categorize_question(question)
        logger.info(f"Question category: {category}")
        
        # Build context prompt
        prompt = self._build_context_prompt(question, job_context, category)
        
        # Try AI providers in order of preference
        answer = None
        ai_provider = "fallback"
        confidence = 0.5
        
        # Try OpenAI first
        if not answer:
            answer = self._query_openai(prompt)
            if answer:
                ai_provider = "openai"
                confidence = 0.9
        
        # Try Anthropic as backup
        if not answer:
            answer = self._query_anthropic(prompt)
            if answer:
                ai_provider = "anthropic"
                confidence = 0.85
        
        # Try Gemini as second backup
        if not answer:
            answer = self._query_gemini(prompt)
            if answer:
                ai_provider = "gemini"
                confidence = 0.8
        
        # Use fallback if all AI providers fail
        if not answer:
            answer = self._get_fallback_answer(question, category)
            ai_provider = "fallback"
            confidence = 0.6
        
        # Create QuestionAnswer object
        qa = QuestionAnswer(
            question=question,
            answer=answer,
            job_title=job_context.get('title', '') if job_context else '',
            company=job_context.get('company', '') if job_context else '',
            timestamp=datetime.now().isoformat(),
            ai_provider=ai_provider,
            confidence=confidence
        )
        
        # Cache the answer
        self._cache_answer(question_hash, qa)
        
        logger.info(f"Generated answer with {ai_provider} (confidence: {confidence})")
        return qa
    
    def bulk_answer_questions(self, questions: List[str], job_context: Dict = None) -> List[QuestionAnswer]:
        """Answer multiple questions at once"""
        answers = []
        for question in questions:
            try:
                answer = self.answer_question(question, job_context)
                answers.append(answer)
            except Exception as e:
                logger.error(f"Error answering question '{question[:50]}...': {e}")
                # Create fallback answer
                fallback_qa = QuestionAnswer(
                    question=question,
                    answer=self._get_fallback_answer(question, "general"),
                    job_title=job_context.get('title', '') if job_context else '',
                    company=job_context.get('company', '') if job_context else '',
                    timestamp=datetime.now().isoformat(),
                    ai_provider="fallback",
                    confidence=0.5
                )
                answers.append(fallback_qa)
        return answers
    
    def get_answer_statistics(self) -> Dict:
        """Get statistics about cached answers"""
        if not self.answers_cache:
            return {"total_questions": 0}
        
        providers = {}
        categories = {}
        companies = {}
        
        for qa_data in self.answers_cache.values():
            # Count by provider
            provider = qa_data.get('ai_provider', 'unknown')
            providers[provider] = providers.get(provider, 0) + 1
            
            # Count by company
            company = qa_data.get('company', 'unknown')
            if company:
                companies[company] = companies.get(company, 0) + 1
        
        return {
            "total_questions": len(self.answers_cache),
            "providers": providers,
            "companies": companies,
            "cache_file": str(self.answers_cache_path)
        }


def main():
    """Demo the AI Question Answerer"""
    print("🤖 AI Question Answerer Demo")
    print("=" * 50)
    
    # Initialize the answerer
    answerer = AIQuestionAnswerer()
    
    # Sample job context
    job_context = {
        "title": "Senior Software Engineer",
        "company": "TechCorp Inc",
        "description": "We are looking for a senior software engineer with expertise in Python, React, and cloud technologies to join our growing team."
    }
    
    # Sample questions
    questions = [
        "Why are you interested in this position?",
        "What relevant experience do you have?",
        "What are your salary expectations?",
        "When can you start?",
        "Are you willing to work remotely?"
    ]
    
    print("\\nAnswering sample questions...")
    for question in questions:
        print(f"\\nQ: {question}")
        answer = answerer.answer_question(question, job_context)
        print(f"A: {answer.answer}")
        print(f"   (Provider: {answer.ai_provider}, Confidence: {answer.confidence})")
    
    # Show statistics
    print(f"\\nCache Statistics:")
    stats = answerer.get_answer_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()