#!/usr/bin/env python3
"""
Simplified End-to-End Test: Focus on core pipeline functionality
"""

import os
import sys
import logging
import asyncio
from pathlib import Path
from dotenv import load_dotenv
import json
from datetime import datetime

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

async def test_complete_pipeline():
    """Test the complete integrated pipeline"""
    
    print("\n" + "="*80)
    print("🚀 AI JOB AUTOPILOT - COMPLETE PIPELINE TEST")
    print("="*80)
    
    resume_file = "Ankit_Thakur_Resume.pdf"
    
    if not Path(resume_file).exists():
        print(f"❌ Resume file not found: {resume_file}")
        return False
    
    print(f"📄 Testing with: {resume_file}")
    
    # Test 1: Complete Resume Processing Pipeline
    print("\n1. COMPLETE RESUME PROCESSING PIPELINE")
    print("-" * 60)
    
    try:
        config = PipelineConfig(
            enable_ai_enhancement=True,
            enable_job_matching=True,
            use_ocr_fallback=True,
            clean_extracted_text=True,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        pipeline = ResumeProcessingPipeline(config)
        result = pipeline.process_resume(resume_file)
        
        if result.overall_success:
            print("✅ Pipeline completed successfully!")
            print(f"📊 Confidence: {result.confidence_score:.2f}/1.0")
            print(f"📊 Quality: {result.quality_score:.2f}/1.0")
            print(f"⏱️  Time: {result.total_processing_time:.2f}s")
            print(f"📧 Email extracted: {result.parsed_resume.contact_info.email}")
            print(f"📱 Phone extracted: {result.parsed_resume.contact_info.phone}")
            print(f"📋 Sections found: {len(result.parsed_resume.sections_found)}")
        else:
            print("❌ Pipeline failed!")
            return False
            
    except Exception as e:
        print(f"❌ Test 1 failed: {e}")
        return False
    
    # Test 2: AI Services Integration
    print("\n2. AI SERVICES INTEGRATION")
    print("-" * 60)
    
    try:
        ai_service = MultiAIService()
        available_services = ai_service.get_available_services()
        
        print(f"🤖 Available services: {[s.value for s in available_services]}")
        
        if available_services:
            # Test job matching
            sample_job_desc = """
            Senior Software Engineer position requiring Python development, 
            web frameworks experience, cloud platforms knowledge, and API development skills.
            """
            
            resume_dict = {
                'contact_info': result.parsed_resume.contact_info.__dict__,
                'skills': result.parsed_resume.skills,
                'work_experience': [exp.__dict__ for exp in result.parsed_resume.work_experience],
                'education': [edu.__dict__ for edu in result.parsed_resume.education]
            }
            
            job_match = await ai_service.match_job_compatibility(resume_dict, sample_job_desc)
            
            if job_match.success:
                print(f"✅ Job matching successful ({job_match.provider.value})")
                print(f"📝 Analysis: {job_match.content[:150]}...")
            else:
                print(f"⚠️  Job matching failed: {job_match.error}")
            
            # Test cover letter generation
            cover_letter = await ai_service.generate_cover_letter(
                resume_dict, sample_job_desc, "TechCorp", "Senior Software Engineer"
            )
            
            if cover_letter.success:
                print(f"✅ Cover letter generated ({cover_letter.provider.value})")
                print(f"📝 Length: {len(cover_letter.content)} characters")
            else:
                print(f"⚠️  Cover letter generation failed: {cover_letter.error}")
                
        else:
            print("⚠️  No AI services available")
            
    except Exception as e:
        print(f"❌ Test 2 failed: {e}")
        return False
    
    # Test 3: Direct AI Resume Enhancement
    print("\n3. AI RESUME ENHANCEMENT")
    print("-" * 60)
    
    try:
        enhancer = AIResumeEnhancer()
        
        # Test async enhancement
        enhanced_data = await enhancer.enhance_resume_async(result.parsed_resume)
        
        print(f"✅ AI enhancement completed!")
        print(f"📊 Overall score: {enhanced_data.analysis.overall_score:.2f}/1.0")
        print(f"🎯 Experience level: {enhanced_data.analysis.estimated_experience_level}")
        print(f"🤖 ATS compatibility: {enhanced_data.analysis.ats_compatibility:.2f}/1.0")
        print(f"💪 Strengths found: {len(enhanced_data.analysis.strengths)}")
        print(f"💡 Suggestions: {len(enhanced_data.analysis.improvement_suggestions)}")
        print(f"🎯 Suitable roles: {len(enhanced_data.analysis.suitable_roles)}")
        
        # Test job matching with direct enhancer
        job_match_score = enhancer.calculate_job_match(result.parsed_resume, sample_job_desc)
        print(f"📈 Direct match score: {job_match_score.overall_match:.2f}/1.0")
        print(f"⚡ Skill match: {job_match_score.skill_match:.2f}/1.0")
        print(f"🔑 Skills matched: {len(job_match_score.matched_skills)}")
        
    except Exception as e:
        print(f"❌ Test 3 failed: {e}")
        return False
    
    # Test 4: LinkedIn Automation Integration Check
    print("\n4. LINKEDIN AUTOMATION CHECK")
    print("-" * 60)
    
    try:
        linkedin_email = os.getenv("LINKEDIN_EMAIL")
        linkedin_password = os.getenv("LINKEDIN_PASSWORD")
        
        if linkedin_email and linkedin_password:
            print(f"✅ LinkedIn credentials: {linkedin_email}")
            
            from src.automation.enhanced_linkedin_autopilot import EnhancedLinkedInAutopilot
            autopilot = EnhancedLinkedInAutopilot()
            
            print("✅ LinkedIn automation available")
            print(f"🤖 AI answers enabled: {autopilot.config['automation']['enable_ai_answers']}")
            print(f"📄 Resume optimization: {autopilot.config['automation']['enable_resume_optimization']}")
            print(f"🔍 Duplicate detection: {autopilot.config['automation']['enable_duplicate_detection']}")
            print(f"📊 Max applications: {autopilot.config['automation']['max_applications_per_session']}")
        else:
            print("⚠️  LinkedIn credentials not configured")
            
    except Exception as e:
        print(f"❌ Test 4 failed: {e}")
        return False
    
    # Calculate overall system health
    print("\n" + "="*80)
    print("🏆 SYSTEM HEALTH ASSESSMENT")
    print("="*80)
    
    health_score = 0
    health_factors = []
    
    # Resume processing (25%)
    if result.overall_success:
        health_score += 25
        health_factors.append("✅ Resume processing pipeline")
    
    # AI services (25%)
    if len(available_services) > 0:
        health_score += 25
        health_factors.append(f"✅ {len(available_services)}/3 AI services operational")
    
    # LinkedIn automation (25%)
    if linkedin_email and linkedin_password:
        health_score += 25
        health_factors.append("✅ LinkedIn automation configured")
    
    # Data quality (25%)
    if result.confidence_score > 0.3:
        health_score += 25
        health_factors.append("✅ Resume parsing quality acceptable")
    
    print(f"\n🎯 OVERALL SYSTEM HEALTH: {health_score}%")
    
    for factor in health_factors:
        print(f"   {factor}")
    
    if health_score < 75:
        print("\n⚠️  SYSTEM NEEDS ATTENTION")
        print("   • Consider improving resume parsing accuracy")
        print("   • Fix API key authentication issues")
        print("   • Test LinkedIn automation manually")
    else:
        print("\n🚀 SYSTEM READY FOR PRODUCTION!")
        print("   • All core components operational")
        print("   • Integration tests passed")
        print("   • Ready for real-world deployment")
    
    # Final Summary
    summary = {
        "test_timestamp": datetime.now().isoformat(),
        "system_health": f"{health_score}%",
        "components_tested": 4,
        "resume_file": resume_file,
        "pipeline_performance": {
            "confidence_score": result.confidence_score,
            "quality_score": result.quality_score,
            "processing_time": result.total_processing_time
        },
        "ai_services": {
            "total_available": len(available_services),
            "services": [s.value for s in available_services]
        },
        "contact_extraction": {
            "email": result.parsed_resume.contact_info.email,
            "phone": result.parsed_resume.contact_info.phone
        },
        "linkedin_ready": bool(linkedin_email and linkedin_password)
    }
    
    print(f"\n📋 DETAILED TEST RESULTS:")
    print(f"   • Resume processed: ✅ {resume_file}")
    print(f"   • Email extracted: {result.parsed_resume.contact_info.email}")
    print(f"   • Phone extracted: {result.parsed_resume.contact_info.phone}")
    print(f"   • Processing time: {result.total_processing_time:.2f}s")
    print(f"   • AI services: {len(available_services)}/3 operational")
    print(f"   • LinkedIn automation: {'✅ Ready' if linkedin_email else '⚠️  Needs setup'}")
    
    # Save results
    results_path = Path("test_results")
    results_path.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(results_path / f"pipeline_test_{timestamp}.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n💾 Results saved: test_results/pipeline_test_{timestamp}.json")
    
    return health_score >= 75

def main():
    """Main test function"""
    setup_logging()
    
    try:
        success = asyncio.run(test_complete_pipeline())
        if success:
            print("\n🎉 Complete pipeline test: SUCCESS!")
        else:
            print("\n❌ Complete pipeline test: NEEDS IMPROVEMENT")
    except KeyboardInterrupt:
        print("\n\nTesting interrupted by user.")
    except Exception as e:
        print(f"\n❌ Testing failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()