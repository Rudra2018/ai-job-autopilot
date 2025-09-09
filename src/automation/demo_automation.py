"""
Demonstration Automation - Shows all capabilities without requiring real login
Perfect for testing and demonstration of the AI Job Autopilot system
"""

import asyncio
import time
import random
from datetime import datetime
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
import logging

@dataclass
class DemoJobApplication:
    job_id: str
    title: str
    company: str
    location: str
    url: str
    status: str
    applied_at: str
    steps_completed: List[str]

class DemoAutomation:
    """Demonstration automation that shows all capabilities"""
    
    def __init__(self, update_callback: Callable = None):
        self.update_callback = update_callback
        self.logger = logging.getLogger(__name__)
        self.applications_today = []
        self.session_stats = {
            'started_at': datetime.now().isoformat(),
            'applications_attempted': 0,
            'applications_successful': 0,
            'applications_failed': 0,
            'platforms_used': []
        }
    
    async def run_full_automation_demo(
        self, 
        target_roles: List[str], 
        target_locations: List[str],
        max_applications: int = 15
    ) -> List[DemoJobApplication]:
        """Run comprehensive automation demonstration"""
        
        await self._send_update("🚀 Starting AI Job Autopilot Demonstration...")
        
        try:
            # Phase 1: Universal Job Scraping
            await self._demo_universal_scraping(target_roles, target_locations)
            
            # Phase 2: AI-Powered Job Matching  
            jobs = await self._demo_ai_job_matching(target_roles, target_locations)
            
            # Phase 3: Universal Auto-Application
            for i, job in enumerate(jobs[:max_applications]):
                success = await self._demo_universal_application(job, i + 1, max_applications)
                if success:
                    self.session_stats['applications_successful'] += 1
                else:
                    self.session_stats['applications_failed'] += 1
                self.session_stats['applications_attempted'] += 1
                
                # Rate limiting demo
                if i < len(jobs) - 1:
                    await self._demo_rate_limiting()
            
            # Phase 4: Results Summary
            await self._demo_results_summary()
            
            return self.applications_today
            
        except Exception as e:
            await self._send_update(f"❌ Demo error: {str(e)}")
            return []
    
    async def _demo_universal_scraping(self, target_roles: List[str], target_locations: List[str]):
        """Demonstrate universal job scraping capabilities"""
        
        await self._send_update("🌍 Initializing Universal Job Scraper...")
        await asyncio.sleep(1)
        
        platforms = [
            ("LinkedIn", "Connecting to LinkedIn API..."),
            ("Indeed", "Accessing Indeed job database..."),
            ("Glassdoor", "Scanning Glassdoor opportunities..."),
            ("Google Career Pages", "Scraping Google jobs directly..."),
            ("Microsoft Careers", "Accessing Microsoft career portal..."),
            ("Amazon Jobs", "Connecting to Amazon job listings..."),
            ("Apple Careers", "Scraping Apple job opportunities..."),
            ("Meta Careers", "Accessing Meta/Facebook jobs..."),
            ("Tesla Jobs", "Scanning Tesla career opportunities..."),
            ("RemoteOK", "Collecting remote job listings..."),
            ("AngelList", "Accessing startup opportunities..."),
            ("Company Career Pages", "Direct scraping from 50+ companies...")
        ]
        
        self.session_stats['platforms_used'] = [p[0] for p in platforms]
        
        for platform, message in platforms:
            await self._send_update(f"🔗 {message}")
            await asyncio.sleep(0.3)
        
        await self._send_update("✅ Connected to 12+ platforms and 50+ company career pages")
        await self._send_update("🎯 Universal scraping active across the entire internet!")
    
    async def _demo_ai_job_matching(self, target_roles: List[str], target_locations: List[str]) -> List[Dict]:
        """Demonstrate AI-powered job matching"""
        
        await self._send_update("🧠 Starting AI-Powered Job Analysis...")
        await asyncio.sleep(1)
        
        # Simulate job discovery
        await self._send_update("🔍 Scanning for cybersecurity opportunities globally...")
        await asyncio.sleep(2)
        
        await self._send_update("🤖 Running NLP analysis on job descriptions...")
        await asyncio.sleep(1.5)
        
        await self._send_update("📊 Calculating skill-match scores using transformer models...")
        await asyncio.sleep(1)
        
        # Generate realistic job data
        companies = [
            {"name": "CrowdStrike", "role": "Senior Penetration Tester", "location": "Remote Worldwide", "match": 97},
            {"name": "Palo Alto Networks", "role": "Cybersecurity Engineer", "location": "San Francisco, CA", "match": 94},
            {"name": "Microsoft", "role": "Cloud Security Architect", "location": "Seattle, WA", "match": 92},
            {"name": "Google", "role": "Information Security Analyst", "location": "London, UK", "match": 90},
            {"name": "Amazon", "role": "DevSecOps Engineer", "location": "Dublin, Ireland", "match": 89},
            {"name": "Tesla", "role": "Application Security Engineer", "location": "Austin, TX", "match": 87},
            {"name": "Meta", "role": "Security Consultant", "location": "Singapore", "match": 85},
            {"name": "Apple", "role": "Threat Intelligence Analyst", "location": "Cupertino, CA", "match": 84},
            {"name": "Okta", "role": "Identity Security Engineer", "location": "Toronto, Canada", "match": 82},
            {"name": "Fortinet", "role": "Network Security Specialist", "location": "Amsterdam, Netherlands", "match": 80}
        ]
        
        jobs = []
        for i, company in enumerate(companies):
            job_data = {
                'id': f"job_{i+1}",
                'title': company['role'],
                'company': company['name'],
                'location': company['location'],
                'url': f"https://{company['name'].lower().replace(' ', '')}.com/careers/job/{i+1}",
                'match_score': company['match'],
                'platform': 'Universal Scraper',
                'salary': f"${80 + i*10}K - ${120 + i*15}K",
                'posted_date': f"{i+1} days ago"
            }
            jobs.append(job_data)
        
        await self._send_update(f"✅ AI Analysis Complete: Found {len(jobs)} high-match opportunities")
        await self._send_update("🎯 Jobs ranked by compatibility score (80%+ match threshold)")
        
        # Show top matches
        for i, job in enumerate(jobs[:3]):
            await self._send_update(f"   {i+1}. {job['title']} at {job['company']} - {job['match_score']}% match")
            await asyncio.sleep(0.5)
        
        return jobs
    
    async def _demo_universal_application(self, job: Dict, current: int, total: int) -> bool:
        """Demonstrate universal auto-application process"""
        
        await self._send_update(f"📝 [{current}/{total}] Applying to: {job['title']} at {job['company']}")
        await asyncio.sleep(0.5)
        
        steps = [
            "🌐 Navigating to company career portal...",
            "🔍 Locating application form...", 
            "🤖 AI analyzing form structure...",
            "📝 Auto-filling personal information...",
            "📋 Inserting experience details...",
            "🎯 Adding relevant skills and certifications...",
            "📄 Generating personalized cover letter...",
            "📎 Attaching optimized resume...",
            "🔍 AI answering custom screening questions...",
            "🚀 Submitting application..."
        ]
        
        completed_steps = []
        for step in steps:
            await self._send_update(f"   {step}")
            completed_steps.append(step)
            await asyncio.sleep(random.uniform(0.3, 0.8))
        
        # Simulate success/failure (95% success rate)
        success = random.random() > 0.05
        
        if success:
            await self._send_update(f"✅ Successfully applied to {job['company']}!")
            
            application = DemoJobApplication(
                job_id=job['id'],
                title=job['title'],
                company=job['company'],
                location=job['location'],
                url=job['url'],
                status='Applied Successfully',
                applied_at=datetime.now().isoformat(),
                steps_completed=completed_steps
            )
            self.applications_today.append(application)
            return True
        else:
            await self._send_update(f"⚠️ Application to {job['company']} requires manual review")
            return False
    
    async def _demo_rate_limiting(self):
        """Demonstrate intelligent rate limiting"""
        
        wait_times = [30, 45, 60, 35, 40]  # Variable timing
        wait_time = random.choice(wait_times)
        
        await self._send_update(f"⏱️ Smart rate limiting: Waiting {wait_time}s to avoid detection...")
        
        # Show countdown for first few seconds
        for remaining in range(min(wait_time, 10), 0, -1):
            await self._send_update(f"   ⏳ {remaining}s remaining...")
            await asyncio.sleep(1)
        
        # Fast forward the rest
        if wait_time > 10:
            await asyncio.sleep(2)  # Simulate the rest quickly
            await self._send_update(f"   ⏳ Rate limiting complete")
        
        await self._send_update("✅ Proceeding to next application...")
    
    async def _demo_results_summary(self):
        """Show final automation results"""
        
        await self._send_update("📊 Generating automation summary...")
        await asyncio.sleep(2)
        
        total_attempted = self.session_stats['applications_attempted']
        total_successful = self.session_stats['applications_successful']
        success_rate = (total_successful / max(total_attempted, 1)) * 100
        
        # Calculate session duration
        start_time = datetime.fromisoformat(self.session_stats['started_at'])
        duration = datetime.now() - start_time
        duration_str = f"{int(duration.total_seconds() / 60)}m {int(duration.total_seconds() % 60)}s"
        
        await self._send_update("🎉 AUTOMATION CAMPAIGN COMPLETED!")
        await self._send_update("=" * 50)
        await self._send_update(f"📈 **RESULTS SUMMARY:**")
        await self._send_update(f"   • Applications Submitted: {total_successful}/{total_attempted}")
        await self._send_update(f"   • Success Rate: {success_rate:.1f}%")
        await self._send_update(f"   • Platforms Used: {len(self.session_stats['platforms_used'])}")
        await self._send_update(f"   • Session Duration: {duration_str}")
        await self._send_update(f"   • Geographic Reach: Global (5 continents)")
        await self._send_update("=" * 50)
        await self._send_update("🚀 AI Job Autopilot demonstration complete!")
        
        # Save demo report
        report = {
            'demo_completed_at': datetime.now().isoformat(),
            'session_stats': self.session_stats,
            'applications': [
                {
                    'company': app.company,
                    'title': app.title,
                    'location': app.location,
                    'status': app.status,
                    'applied_at': app.applied_at
                }
                for app in self.applications_today
            ]
        }
        
        import json
        with open(f"demo_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", 'w') as f:
            json.dump(report, f, indent=2)
        
        await self._send_update(f"📄 Detailed report saved: demo_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    
    async def _send_update(self, message: str):
        """Send progress update"""
        
        if self.update_callback:
            await self.update_callback({
                'timestamp': datetime.now().isoformat(),
                'message': message,
                'level': 'info'
            })
        
        self.logger.info(message)
        print(f"[DEMO] {message}")  # Also print for console visibility

# Convenience function
async def run_automation_demo(
    target_roles: List[str],
    target_locations: List[str], 
    max_applications: int = 10,
    update_callback: Callable = None
) -> List[DemoJobApplication]:
    """Run complete automation demonstration"""
    
    demo = DemoAutomation(update_callback)
    return await demo.run_full_automation_demo(target_roles, target_locations, max_applications)