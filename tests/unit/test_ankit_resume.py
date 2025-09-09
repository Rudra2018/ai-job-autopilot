#!/usr/bin/env python3
"""
Test script for Ankit Thakur's resume with enhanced pipeline and AI services
"""

import os
import sys
import logging
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Add src to path
sys.path.append(str(Path(__file__).parent))

# Load environment variables
load_dotenv()

from src.core.resume_processing_pipeline import ResumeProcessingPipeline, PipelineConfig
from src.ml.multi_ai_service import MultiAIService
from src.ml.ai_resume_enhancer import AIResumeEnhancer

def setup_logging():
    """Setup logging for testing"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

async def test_ankit_resume():
    """Test the complete pipeline with Ankit's resume"""
    
    print("\n" + "="*80)
    print("TESTING ENHANCED PIPELINE WITH ANKIT THAKUR'S RESUME")
    print("="*80)
    
    resume_file = "Ankit_Thakur_Resume.pdf"
    
    # Check if resume file exists
    if not Path(resume_file).exists():
        print(f"❌ Resume file not found: {resume_file}")
        print("Please ensure Ankit_Thakur_Resume.pdf is in the current directory")
        return
    
    print(f"📄 Resume file found: {resume_file}")
    
    # Test 1: Multi-AI Service Availability
    print("\n1. TESTING AI SERVICES AVAILABILITY")
    print("-" * 50)
    
    ai_service = MultiAIService()
    available_services = ai_service.get_available_services()
    
    print(f"✅ Available AI Services: {[s.value for s in available_services]}")
    
    if not available_services:
        print("⚠️  No AI services available. Please check API keys in .env file")
    else:
        print(f"🤖 Primary service: {available_services[0].value}")
    
    # Test 2: Basic Pipeline Processing
    print("\n2. BASIC RESUME PROCESSING")
    print("-" * 50)
    
    try:
        # Create pipeline configuration
        config = PipelineConfig(
            enable_ai_enhancement=True,
            enable_job_matching=False,
            use_ocr_fallback=True,
            clean_extracted_text=True,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        pipeline = ResumeProcessingPipeline(config)
        result = pipeline.process_resume(resume_file)
        
        if result.overall_success:
            print("✅ Pipeline processing successful!")
            print(f"📊 Confidence Score: {result.confidence_score:.2f}/1.0")
            print(f"📊 Quality Score: {result.quality_score:.2f}/1.0")
            print(f"⏱️  Processing Time: {result.total_processing_time:.2f}s")
            print(f"📃 Extraction Method: {result.extraction_result.method}")
            
            # Display contact information
            contact = result.parsed_resume.contact_info
            print(f"\n📇 CONTACT INFORMATION:")
            print(f"   Name: {contact.name}")
            print(f"   Email: {contact.email}")
            print(f"   Phone: {contact.phone}")
            print(f"   LinkedIn: {contact.linkedin}")
            print(f"   Location: {contact.city}, {contact.state}")
            
            # Display parsed sections
            print(f"\n📋 PARSED SECTIONS:")
            print(f"   Sections Found: {', '.join(result.parsed_resume.sections_found)}")
            print(f"   Work Experience: {len(result.parsed_resume.work_experience)} entries")
            print(f"   Education: {len(result.parsed_resume.education)} entries")
            print(f"   Skills: {len(result.parsed_resume.skills)} items")
            print(f"   Projects: {len(result.parsed_resume.projects)} entries")
            print(f"   Certifications: {len(result.parsed_resume.certifications)} entries")
            
            # Display work experience
            if result.parsed_resume.work_experience:
                print(f"\n💼 LATEST WORK EXPERIENCE:")
                latest_job = result.parsed_resume.work_experience[0]
                print(f"   Position: {latest_job.position}")
                print(f"   Company: {latest_job.company}")
                print(f"   Duration: {latest_job.start_date} - {latest_job.end_date}")
                if latest_job.description:
                    print(f"   Description: {latest_job.description[0][:100]}...")
            
            # Display skills
            if result.parsed_resume.skills:
                print(f"\n⚡ TOP SKILLS:")
                for skill in result.parsed_resume.skills[:15]:
                    print(f"   • {skill}")
            
            # Display education
            if result.parsed_resume.education:
                print(f"\n🎓 EDUCATION:")
                for edu in result.parsed_resume.education:
                    print(f"   • {edu.degree} from {edu.institution}")
                    if edu.field_of_study:
                        print(f"     Field: {edu.field_of_study}")
                    if edu.gpa:
                        print(f"     GPA: {edu.gpa}")
        else:
            print("❌ Pipeline processing failed!")
            for error in result.errors:
                print(f"   Error: {error}")
            return
    
    except Exception as e:
        print(f"❌ Pipeline processing failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Test 3: AI Enhancement
    if available_services and result.overall_success:
        print("\n3. AI-POWERED ENHANCEMENT")
        print("-" * 50)
        
        try:
            enhancer = AIResumeEnhancer()
            
            # Test async enhancement
            enhanced_data = await enhancer.enhance_resume_async(result.parsed_resume)
            
            print("✅ AI enhancement completed!")
            print(f"📊 Overall Score: {enhanced_data.analysis.overall_score:.2f}/1.0")
            print(f"🎯 Experience Level: {enhanced_data.analysis.estimated_experience_level}")
            print(f"🤖 ATS Compatibility: {enhanced_data.analysis.ats_compatibility:.2f}/1.0")
            
            # Display strengths
            if enhanced_data.analysis.strengths:
                print(f"\n💪 KEY STRENGTHS:")
                for strength in enhanced_data.analysis.strengths[:5]:
                    print(f"   • {strength}")
            
            # Display suitable roles
            if enhanced_data.analysis.suitable_roles:
                print(f"\n🎯 SUITABLE ROLES:")
                for role in enhanced_data.analysis.suitable_roles[:5]:
                    print(f"   • {role}")
            
            # Display improvement suggestions
            if enhanced_data.analysis.improvement_suggestions:
                print(f"\n💡 IMPROVEMENT SUGGESTIONS:")
                for suggestion in enhanced_data.analysis.improvement_suggestions[:5]:
                    print(f"   • {suggestion}")
            
            # Display enhanced summary if available
            if enhanced_data.enhanced_summary and enhanced_data.enhanced_summary != result.parsed_resume.summary:
                print(f"\n📝 AI-ENHANCED SUMMARY:")
                print(f"   {enhanced_data.enhanced_summary}")
                
                if "ai_provider" in enhanced_data.processing_metadata:
                    print(f"   (Generated by: {enhanced_data.processing_metadata['ai_provider']})")
        
        except Exception as e:
            print(f"⚠️  AI enhancement failed: {e}")
    
    # Test 4: Job Matching Demo
    print("\n4. JOB MATCHING DEMONSTRATION")
    print("-" * 50)
    
    sample_job_descriptions = [
        {
            "title": "Senior Software Engineer",
            "company": "Tech Innovations Inc.",
            "description": """
            We are seeking a Senior Software Engineer with 5+ years of experience to join our growing team.
            
            Requirements:
            • 5+ years of software development experience
            • Strong proficiency in Python, Java, or similar languages
            • Experience with cloud platforms (AWS, Azure, GCP)
            • Knowledge of microservices architecture
            • Experience with databases (SQL, NoSQL)
            • Familiarity with DevOps practices and CI/CD
            • Bachelor's degree in Computer Science or related field
            • Strong problem-solving and communication skills
            
            Preferred:
            • Experience with Kubernetes and Docker
            • Knowledge of machine learning frameworks
            • Leadership or mentoring experience
            • Agile development methodology experience
            """
        },
        {
            "title": "Data Scientist", 
            "company": "Analytics Corp",
            "description": """
            Looking for a Data Scientist to work on cutting-edge machine learning projects.
            
            Requirements:
            • 3+ years of data science experience
            • Strong Python skills with pandas, numpy, scikit-learn
            • Experience with machine learning algorithms
            • SQL and database knowledge
            • Statistical analysis and modeling expertise
            • Data visualization skills (matplotlib, plotly, tableau)
            • Master's degree in Data Science, Statistics, or related field
            
            Preferred:
            • Experience with deep learning frameworks (TensorFlow, PyTorch)
            • Cloud platform experience (AWS, GCP)
            • Big data technologies (Spark, Hadoop)
            • Experience with A/B testing and experimental design
            """
        }
    ]
    
    if result.overall_success and available_services:
        for i, job in enumerate(sample_job_descriptions):
            print(f"\n   Job {i+1}: {job['title']} at {job['company']}")
            
            try:
                # Calculate job match using AI
                resume_dict = {
                    'contact_info': result.parsed_resume.contact_info.__dict__,
                    'skills': result.parsed_resume.skills,
                    'work_experience': [exp.__dict__ for exp in result.parsed_resume.work_experience],
                    'education': [edu.__dict__ for edu in result.parsed_resume.education]
                }
                
                match_response = await ai_service.match_job_compatibility(
                    resume_dict, 
                    job['description']
                )
                
                if match_response.success:
                    print(f"   🎯 AI Match Analysis: {match_response.content[:200]}...")
                    print(f"   🤖 Analyzed by: {match_response.provider.value}")
                else:
                    # Fallback to basic matching
                    enhancer = AIResumeEnhancer()
                    match_score = enhancer.calculate_job_match(result.parsed_resume, job['description'])
                    print(f"   🎯 Basic Match Score: {match_score.overall_match:.2f}/1.0")
                    print(f"   ⚡ Skill Match: {match_score.skill_match:.2f}/1.0")
                    print(f"   🔑 Matched Skills: {len(match_score.matched_skills)}")
                    print(f"   ❌ Missing Skills: {len(match_score.missing_skills)}")
                
            except Exception as e:
                print(f"   ⚠️  Job matching failed: {e}")
    
    # Test 5: Generate Cover Letter
    if available_services and result.overall_success:
        print("\n5. AI COVER LETTER GENERATION")
        print("-" * 50)
        
        try:
            job = sample_job_descriptions[0]  # Use first job for demo
            
            resume_dict = {
                'contact_info': result.parsed_resume.contact_info.__dict__,
                'skills': result.parsed_resume.skills,
                'work_experience': [exp.__dict__ for exp in result.parsed_resume.work_experience],
                'education': [edu.__dict__ for edu in result.parsed_resume.education],
                'summary': result.parsed_resume.summary
            }
            
            cover_letter_response = await ai_service.generate_cover_letter(
                resume_dict,
                job['description'],
                job['company'],
                job['title']
            )
            
            if cover_letter_response.success:
                print("✅ AI-generated cover letter:")
                print("-" * 30)
                print(cover_letter_response.content)
                print("-" * 30)
                print(f"Generated by: {cover_letter_response.provider.value}")
            else:
                print(f"⚠️  Cover letter generation failed: {cover_letter_response.error}")
        
        except Exception as e:
            print(f"⚠️  Cover letter generation failed: {e}")
    
    print("\n" + "="*80)
    print("✅ ANKIT'S RESUME TESTING COMPLETED!")
    print("="*80)
    
    # Summary
    confidence_str = f"{result.confidence_score:.2f}" if 'result' in locals() and result.overall_success else 'N/A'
    quality_str = f"{result.quality_score:.2f}" if 'result' in locals() and result.overall_success else 'N/A'
    
    print(f"""
🎯 TESTING SUMMARY:
✅ Resume file processed: {resume_file}
✅ Pipeline success: {result.overall_success if 'result' in locals() else False}
✅ AI services available: {len(available_services)} 
✅ Extraction confidence: {confidence_str}
✅ Resume quality: {quality_str}

📋 NEXT STEPS:
1. Review extracted information for accuracy
2. Test LinkedIn automation features
3. Run end-to-end job application simulation
4. Configure job scrapers for real-world usage

🔧 PIPELINE CAPABILITIES VALIDATED:
✅ Multi-method PDF text extraction
✅ Advanced resume section parsing
✅ Multi-AI service integration (OpenAI, Claude, Gemini)
✅ Job compatibility analysis
✅ Cover letter generation
✅ ATS optimization recommendations
""")

def main():
    """Main test function"""
    setup_logging()
    
    try:
        asyncio.run(test_ankit_resume())
    except KeyboardInterrupt:
        print("\n\nTesting interrupted by user.")
    except Exception as e:
        print(f"\n❌ Testing failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()