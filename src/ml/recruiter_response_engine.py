#!/usr/bin/env python3
"""
Recruiter Response Engine - AI-powered recruiter communication management
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

class RecruiterResponseEngine:
    def __init__(self):
        self.response_templates = {
            'initial_interest': {
                'subject_templates': [
                    'Re: Interest in {job_title} Position',
                    'Thank you for reaching out - {job_title} Opportunity',
                    'Following up on {job_title} Discussion'
                ],
                'response_templates': [
                    "Thank you for reaching out about the {job_title} position at {company}. I'm very interested in learning more about this opportunity. My {experience_years} years of experience in {primary_skills} aligns well with what you're looking for. I'd be happy to schedule a call to discuss how I can contribute to your team.",
                    "I appreciate you considering me for the {job_title} role. Based on the requirements you shared, my background in {primary_skills} and proven track record in {industry} makes me a strong candidate. I'm excited to explore this opportunity further and would welcome a conversation about next steps.",
                    "Thank you for the {job_title} opportunity at {company}. I'm definitely interested in learning more. My expertise in {primary_skills} and {experience_years}+ years in {industry} position me well for this role. Please let me know your availability for a brief call to discuss the position in detail."
                ]
            },
            'scheduling_response': {
                'subject_templates': [
                    'Re: Interview Scheduling for {job_title}',
                    'Available Times - {job_title} Interview',
                    'Scheduling Confirmation - {company} Interview'
                ],
                'response_templates': [
                    "Thank you for the interview invitation. I'm available for the {job_title} interview on the following dates and times:\n\n• {time_slot_1}\n• {time_slot_2}\n• {time_slot_3}\n\nPlease let me know which works best for your schedule. I look forward to our conversation.",
                    "I'm excited about the opportunity to interview for the {job_title} position. My availability this week includes:\n\n• {time_slot_1}\n• {time_slot_2}\n• {time_slot_3}\n\nI'm flexible and can accommodate other times if needed. Looking forward to speaking with you soon.",
                    "Thank you for scheduling the interview for {job_title}. I can accommodate any of these time slots:\n\n• {time_slot_1}\n• {time_slot_2}\n• {time_slot_3}\n\nPlease confirm which time works best. I'm looking forward to discussing how I can contribute to {company}."
                ]
            },
            'follow_up': {
                'subject_templates': [
                    'Following up on {job_title} Application',
                    'Checking in - {job_title} Position Status',
                    'Update on {company} Application'
                ],
                'response_templates': [
                    "I wanted to follow up on my application for the {job_title} position at {company}. I remain very interested in this opportunity and would appreciate any updates on the selection process. Please let me know if you need any additional information from me.",
                    "I hope this email finds you well. I'm writing to check on the status of my application for the {job_title} role. I'm still very enthusiastic about joining {company} and contributing to your team. I'm happy to provide any additional materials or references if needed.",
                    "I wanted to touch base regarding the {job_title} position we discussed. I'm still very interested and excited about the possibility of joining {company}. If there are any updates on the timeline or next steps, I'd love to hear from you."
                ]
            },
            'thank_you': {
                'subject_templates': [
                    'Thank you - {job_title} Interview',
                    'Following up on our {job_title} Discussion',
                    'Thank you for your time - {company} Interview'
                ],
                'response_templates': [
                    "Thank you for taking the time to interview me for the {job_title} position today. I enjoyed our conversation about {discussion_topic} and am even more excited about the opportunity to contribute to {company}. I look forward to hearing about next steps.",
                    "I wanted to thank you for the insightful interview for the {job_title} role. Our discussion about {discussion_topic} reinforced my interest in joining your team. I'm confident my experience in {primary_skills} would be valuable to {company}. Please let me know if you need any additional information.",
                    "Thank you for the engaging interview today. I appreciate the time you took to discuss the {job_title} position and share insights about {company}'s vision. I'm very interested in moving forward and contributing to your continued success."
                ]
            },
            'negotiation': {
                'subject_templates': [
                    'Re: {job_title} Offer Discussion',
                    'Thank you for the offer - {job_title}',
                    '{job_title} Compensation Discussion'
                ],
                'response_templates': [
                    "Thank you for the offer for the {job_title} position. I'm excited about joining {company} and contributing to your team. Based on my {experience_years} years of experience and market research, I'd like to discuss the compensation package. Would you be open to a brief conversation about this?",
                    "I'm thrilled about the {job_title} opportunity at {company}. After reviewing the offer, I'd like to discuss a few aspects of the compensation package to ensure it aligns with my experience level and market standards. I'm confident we can reach a mutually beneficial agreement.",
                    "Thank you for the generous offer for the {job_title} role. I'm very interested in accepting and joining {company}. I'd appreciate the opportunity to discuss the overall compensation package to ensure it reflects my {experience_years} years of experience in {primary_skills}."
                ]
            }
        }
        
        self.communication_contexts = {
            'phone_screen': ['initial screening', 'basic qualifications', 'company culture'],
            'technical_interview': ['technical skills', 'problem-solving approach', 'code review'],
            'behavioral_interview': ['past experiences', 'team collaboration', 'leadership examples'],
            'final_interview': ['company vision', 'long-term goals', 'cultural fit']
        }
    
    def generate_response(self, recruiter_message: str, context: Dict[str, Any], response_type: str) -> Dict[str, Any]:
        """Generate contextual response to recruiter communication"""
        
        # Extract context information
        job_title = context.get('job_title', 'the position')
        company = context.get('company', 'your company')
        user_profile = context.get('user_profile', {})
        
        # Get user data
        experience_years = user_profile.get('total_experience', {}).get('total_years', 0)
        skills = user_profile.get('skills', {})
        industries = user_profile.get('industries', [])
        primary_skills = self.get_primary_skills(skills)
        industry = industries[0] if industries else 'technology'
        
        # Generate response based on type
        if response_type not in self.response_templates:
            response_type = 'initial_interest'
        
        template_data = self.response_templates[response_type]
        
        # Select templates
        subject = random.choice(template_data['subject_templates'])
        response = random.choice(template_data['response_templates'])
        
        # Generate time slots for scheduling
        time_slots = self.generate_time_slots() if response_type == 'scheduling_response' else []
        
        # Format templates
        format_vars = {
            'job_title': job_title,
            'company': company,
            'experience_years': experience_years,
            'primary_skills': ', '.join(primary_skills[:3]),
            'industry': industry.lower(),
            'discussion_topic': self.generate_discussion_topic(response_type),
            'time_slot_1': time_slots[0] if len(time_slots) > 0 else '',
            'time_slot_2': time_slots[1] if len(time_slots) > 1 else '',
            'time_slot_3': time_slots[2] if len(time_slots) > 2 else ''
        }
        
        try:
            formatted_subject = subject.format(**format_vars)
            formatted_response = response.format(**format_vars)
        except KeyError:
            # Fallback if formatting fails
            formatted_subject = f"Re: {job_title} Opportunity"
            formatted_response = f"Thank you for reaching out about the {job_title} position. I'm interested in learning more."
        
        return {
            'response_type': response_type,
            'subject': formatted_subject,
            'response': formatted_response,
            'tone': self.determine_tone(response_type),
            'urgency': self.determine_urgency(response_type),
            'generated_at': datetime.now().isoformat(),
            'context_used': {
                'job_title': job_title,
                'company': company,
                'user_experience': f"{experience_years} years",
                'primary_skills': primary_skills[:3]
            }
        }
    
    def get_primary_skills(self, skills: Dict[str, List[str]]) -> List[str]:
        """Extract primary skills from user profile"""
        primary = []
        for category, skill_list in skills.items():
            if skill_list and category != 'soft_skills':
                primary.extend(skill_list[:2])
        return primary[:4]  # Return top 4 primary skills
    
    def generate_time_slots(self) -> List[str]:
        """Generate available time slots for scheduling"""
        slots = []
        base_date = datetime.now() + timedelta(days=1)
        
        for i in range(3):
            date = base_date + timedelta(days=i)
            morning_time = "10:00 AM"
            afternoon_time = "2:00 PM"
            
            slots.append(f"{date.strftime('%A, %B %d')} at {morning_time} EST")
            if len(slots) < 3:
                slots.append(f"{date.strftime('%A, %B %d')} at {afternoon_time} EST")
        
        return slots[:3]
    
    def generate_discussion_topic(self, response_type: str) -> str:
        """Generate relevant discussion topic based on response type"""
        topics = {
            'thank_you': ['the team structure', 'upcoming projects', 'company growth plans', 'technology stack'],
            'initial_interest': ['role requirements', 'team dynamics', 'growth opportunities'],
            'follow_up': ['application timeline', 'next steps', 'additional requirements']
        }
        
        topic_list = topics.get(response_type, ['the opportunity'])
        return random.choice(topic_list)
    
    def determine_tone(self, response_type: str) -> str:
        """Determine appropriate tone for response type"""
        tone_mapping = {
            'initial_interest': 'professional_enthusiastic',
            'scheduling_response': 'accommodating_professional',
            'follow_up': 'polite_persistent',
            'thank_you': 'grateful_professional',
            'negotiation': 'confident_respectful'
        }
        return tone_mapping.get(response_type, 'professional')
    
    def determine_urgency(self, response_type: str) -> str:
        """Determine response urgency"""
        urgency_mapping = {
            'scheduling_response': 'high',
            'negotiation': 'medium',
            'initial_interest': 'medium',
            'follow_up': 'low',
            'thank_you': 'high'
        }
        return urgency_mapping.get(response_type, 'medium')
    
    def analyze_recruiter_message(self, message: str) -> Dict[str, Any]:
        """Analyze recruiter message to determine context and response type"""
        message_lower = message.lower()
        
        # Determine message type
        if any(word in message_lower for word in ['schedule', 'interview', 'call', 'meeting']):
            response_type = 'scheduling_response'
        elif any(word in message_lower for word in ['offer', 'compensation', 'salary', 'package']):
            response_type = 'negotiation'
        elif any(word in message_lower for word in ['thank', 'interview', 'spoke', 'talked']):
            response_type = 'thank_you'
        elif any(word in message_lower for word in ['follow up', 'status', 'update', 'timeline']):
            response_type = 'follow_up'
        else:
            response_type = 'initial_interest'
        
        # Extract entities
        urgency_indicators = ['urgent', 'asap', 'immediately', 'today', 'tomorrow']
        is_urgent = any(indicator in message_lower for indicator in urgency_indicators)
        
        return {
            'detected_type': response_type,
            'urgency': 'high' if is_urgent else 'medium',
            'key_topics': self.extract_key_topics(message),
            'sentiment': self.analyze_sentiment(message_lower)
        }
    
    def extract_key_topics(self, message: str) -> List[str]:
        """Extract key topics from recruiter message"""
        message_lower = message.lower()
        topics = []
        
        topic_keywords = {
            'interview': ['interview', 'call', 'discussion', 'chat'],
            'timeline': ['timeline', 'when', 'schedule', 'date'],
            'requirements': ['requirements', 'qualifications', 'skills', 'experience'],
            'compensation': ['salary', 'compensation', 'package', 'benefits'],
            'next_steps': ['next steps', 'process', 'stages', 'rounds']
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                topics.append(topic)
        
        return topics
    
    def analyze_sentiment(self, message: str) -> str:
        """Basic sentiment analysis of recruiter message"""
        positive_words = ['excited', 'great', 'excellent', 'impressive', 'interested', 'pleased']
        negative_words = ['unfortunately', 'concern', 'issue', 'problem', 'difficult']
        
        positive_count = sum(1 for word in positive_words if word in message)
        negative_count = sum(1 for word in negative_words if word in message)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'
    
    def generate_conversation_thread(self, initial_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate a realistic conversation thread with recruiter"""
        thread = []
        
        # Initial recruiter outreach (simulated)
        thread.append({
            'sender': 'recruiter',
            'message': f"Hi! I came across your profile and think you'd be a great fit for our {initial_context.get('job_title', 'Software Engineer')} role at {initial_context.get('company', 'TechCorp')}. Are you open to discussing this opportunity?",
            'timestamp': datetime.now().isoformat()
        })
        
        # Generate initial response
        response = self.generate_response('', initial_context, 'initial_interest')
        thread.append({
            'sender': 'user',
            'subject': response['subject'],
            'message': response['response'],
            'timestamp': (datetime.now() + timedelta(hours=2)).isoformat()
        })
        
        return thread
    
    def process_recruiter_communication(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Main method to process recruiter communication"""
        
        # Analyze the message
        analysis = self.analyze_recruiter_message(message)
        
        # Generate appropriate response
        response = self.generate_response(message, context, analysis['detected_type'])
        
        # Calculate response timing
        response_timing = self.calculate_response_timing(analysis['urgency'])
        
        return {
            'communication_status': 'processed',
            'analysis': analysis,
            'generated_response': response,
            'recommended_timing': response_timing,
            'follow_up_suggestions': self.suggest_follow_up_actions(analysis['detected_type']),
            'processed_at': datetime.now().isoformat()
        }
    
    def calculate_response_timing(self, urgency: str) -> Dict[str, Any]:
        """Calculate optimal response timing based on urgency"""
        timing_map = {
            'high': {
                'min_delay_hours': 1,
                'max_delay_hours': 4,
                'recommended': 'Respond within 2-4 hours'
            },
            'medium': {
                'min_delay_hours': 4,
                'max_delay_hours': 24,
                'recommended': 'Respond within 4-8 hours'
            },
            'low': {
                'min_delay_hours': 12,
                'max_delay_hours': 48,
                'recommended': 'Respond within 12-24 hours'
            }
        }
        
        return timing_map.get(urgency, timing_map['medium'])
    
    def suggest_follow_up_actions(self, response_type: str) -> List[str]:
        """Suggest follow-up actions based on response type"""
        actions = {
            'initial_interest': [
                'Research the company and role thoroughly',
                'Prepare questions about team structure and projects',
                'Review and update portfolio/GitHub if relevant'
            ],
            'scheduling_response': [
                'Confirm interview details and format',
                'Prepare for common interview questions',
                'Research the interviewer if name is provided'
            ],
            'thank_you': [
                'Send LinkedIn connection request',
                'Research mentioned projects or technologies',
                'Prepare for potential next round'
            ],
            'negotiation': [
                'Research market rates for similar positions',
                'Prepare justification for requested compensation',
                'Consider entire package, not just base salary'
            ]
        }
        
        return actions.get(response_type, ['Monitor for recruiter response', 'Continue job search activities'])

# Global instance for use in Streamlit
recruiter_response_engine = RecruiterResponseEngine()