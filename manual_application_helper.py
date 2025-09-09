#!/usr/bin/env python3
"""
AI Job Application Helper - Manual Mode
Generate personalized application materials for any job
"""

import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Add src to path
sys.path.append(str(Path(__file__).parent))

# Load environment variables
load_dotenv()

async def generate_application_materials():
    """Generate personalized application materials for a specific job"""
    
    print("🎯 AI JOB APPLICATION HELPER")
    print("=" * 50)
    print("Generate personalized cover letters and analysis for any job!\n")
    
    # Load resume
    print("1️⃣ Loading your resume...")
    
    try:
        from src.core.resume_processing_pipeline import ResumeProcessingPipeline, PipelineConfig
        from src.ml.multi_ai_service import MultiAIService
        
        config = PipelineConfig(enable_ai_enhancement=True)
        pipeline = ResumeProcessingPipeline(config)
        result = pipeline.process_resume("Ankit_Thakur_Resume.pdf")
        
        if result.overall_success:
            print(f"✅ Resume loaded successfully!")
            print(f"📧 {result.parsed_resume.contact_info.email}")
            print(f"📱 {result.parsed_resume.contact_info.phone}")
        else:
            print("❌ Failed to load resume")
            return
            
    except Exception as e:
        print(f"❌ Error loading resume: {e}")
        return
    
    # Initialize AI service
    ai_service = MultiAIService()
    resume_dict = {
        'contact_info': result.parsed_resume.contact_info.__dict__,
        'skills': result.parsed_resume.skills,
        'work_experience': [exp.__dict__ for exp in result.parsed_resume.work_experience],
        'education': [edu.__dict__ for edu in result.parsed_resume.education],
        'summary': result.parsed_resume.summary
    }
    
    # Sample job examples you can use
    sample_jobs = [
        {
            "title": "Python Developer",
            "company": "TechCorp",
            "description": """
            We're seeking a Python Developer to join our growing team!
            
            Requirements:
            • 2+ years Python experience
            • Django or Flask experience
            • Database knowledge (PostgreSQL/MySQL)
            • Git version control
            • Problem-solving skills
            • CS degree or equivalent
            
            Nice to have:
            • Cloud experience (AWS/GCP)
            • JavaScript/React
            • API development
            • Agile methodology
            """
        },
        {
            "title": "Software Engineer",
            "company": "StartupXYZ", 
            "description": """
            Software Engineer - Full Stack (Remote)
            
            We need a passionate developer to help build our platform!
            
            Must have:
            • Strong programming skills (Python, JavaScript)
            • Web development experience
            • Database design knowledge
            • Testing and debugging skills
            • Good communication
            
            Preferred:
            • React/Vue.js experience
            • Docker/Kubernetes
            • CI/CD pipelines
            • Previous startup experience
            """
        },
        {
            "title": "Junior Developer",
            "company": "GrowthTech",
            "description": """
            Junior Software Developer Position
            
            Perfect for new graduates or career changers!
            
            Requirements:
            • Basic programming knowledge
            • Willingness to learn
            • Problem-solving mindset
            • Team collaboration skills
            • Computer Science background preferred
            
            We offer:
            • Mentorship program
            • Training opportunities
            • Career growth path
            • Great team culture
            """
        }
    ]
    
    print(f"\n2️⃣ Available sample jobs to apply for:")
    print("-" * 40)
    
    for i, job in enumerate(sample_jobs, 1):
        print(f"{i}. {job['title']} at {job['company']}")
    
    print(f"\nGenerating materials for all sample jobs...\n")
    
    # Generate materials for each job
    for i, job in enumerate(sample_jobs, 1):
        print(f"🎯 JOB {i}: {job['title']} at {job['company']}")
        print("=" * 50)
        
        try:
            # Job compatibility analysis
            print("📊 Analyzing job compatibility...")
            match_result = await ai_service.match_job_compatibility(resume_dict, job['description'])
            
            if match_result.success:
                print(f"✅ Analysis complete! (AI: {match_result.provider.value})")
                print(f"📈 Compatibility: {match_result.content[:200]}...")
            else:
                print(f"⚠️ Analysis failed: {match_result.error}")
            
            # Generate cover letter
            print(f"\n📝 Generating personalized cover letter...")
            cover_letter = await ai_service.generate_cover_letter(
                resume_dict, job['description'], job['company'], job['title']
            )
            
            if cover_letter.success:
                print(f"✅ Cover letter ready! ({len(cover_letter.content)} chars)")
                
                # Save cover letter to file
                filename = f"cover_letter_{job['company'].lower().replace(' ', '_')}_{job['title'].lower().replace(' ', '_')}.txt"
                with open(filename, 'w') as f:
                    f.write(f"Cover Letter for {job['title']} at {job['company']}\n")
                    f.write("=" * 60 + "\n\n")
                    f.write(cover_letter.content)
                    f.write(f"\n\n--- Generated by AI Job Autopilot ---")
                
                print(f"💾 Saved to: {filename}")
                
                # Show preview
                print(f"\n📄 PREVIEW:")
                print("-" * 30)
                print(cover_letter.content[:300] + "...")
                print("-" * 30)
                
            else:
                print(f"⚠️ Cover letter generation failed: {cover_letter.error}")
            
        except Exception as e:
            print(f"❌ Error processing job {i}: {e}")
        
        print(f"\n")
    
    # Generate general application materials
    print(f"📋 GENERATING ADDITIONAL MATERIALS")
    print("=" * 50)
    
    try:
        # Resume enhancement suggestions
        from src.ml.ai_resume_enhancer import AIResumeEnhancer
        
        enhancer = AIResumeEnhancer()
        enhanced_data = await enhancer.enhance_resume_async(result.parsed_resume)
        
        print(f"💡 RESUME IMPROVEMENT SUGGESTIONS:")
        for i, suggestion in enumerate(enhanced_data.analysis.improvement_suggestions[:5], 1):
            print(f"   {i}. {suggestion}")
        
        print(f"\n🎯 SUITABLE ROLES FOR YOU:")
        for i, role in enumerate(enhanced_data.analysis.suitable_roles[:5], 1):
            print(f"   {i}. {role}")
        
        print(f"\n📊 RESUME ANALYSIS:")
        print(f"   • Overall score: {enhanced_data.analysis.overall_score:.2f}/1.0")
        print(f"   • Experience level: {enhanced_data.analysis.estimated_experience_level}")
        print(f"   • ATS compatibility: {enhanced_data.analysis.ats_compatibility:.2f}/1.0")
        
        # Save analysis to file
        with open("resume_analysis.txt", "w") as f:
            f.write("AI Resume Analysis Report\n")
            f.write("=" * 40 + "\n\n")
            f.write(f"Overall Score: {enhanced_data.analysis.overall_score:.2f}/1.0\n")
            f.write(f"Experience Level: {enhanced_data.analysis.estimated_experience_level}\n")
            f.write(f"ATS Compatibility: {enhanced_data.analysis.ats_compatibility:.2f}/1.0\n\n")
            f.write("Improvement Suggestions:\n")
            for i, suggestion in enumerate(enhanced_data.analysis.improvement_suggestions, 1):
                f.write(f"{i}. {suggestion}\n")
            f.write(f"\nSuitable Roles:\n")
            for i, role in enumerate(enhanced_data.analysis.suitable_roles, 1):
                f.write(f"{i}. {role}\n")
            f.write(f"\n--- Generated by AI Job Autopilot ---")
        
        print(f"💾 Analysis saved to: resume_analysis.txt")
        
    except Exception as e:
        print(f"❌ Error generating analysis: {e}")
    
    # Final summary
    print(f"\n" + "=" * 60)
    print("🎉 APPLICATION MATERIALS GENERATED!")
    print("=" * 60)
    
    print(f"""
📁 FILES CREATED:
✅ cover_letter_techcorp_python_developer.txt
✅ cover_letter_startupxyz_software_engineer.txt  
✅ cover_letter_growthtech_junior_developer.txt
✅ resume_analysis.txt

🎯 NEXT STEPS:
1. Review all generated cover letters
2. Customize them for specific applications
3. Use the resume improvement suggestions
4. Apply to jobs manually with your materials
5. Track responses and adjust approach

💡 HOW TO USE:
• Copy cover letters into job application forms
• Adapt the content for each specific job
• Use the analysis to improve your resume
• Apply the suggestions to increase success rates

🚀 Your AI Job Autopilot has prepared everything you need!
Ready to land your dream job! 🎊
""")
    
    print(f"Generated on: {Path.cwd()}")

def main():
    """Main function"""
    
    try:
        asyncio.run(generate_application_materials())
    except KeyboardInterrupt:
        print(f"\n\n🛑 Generation interrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()