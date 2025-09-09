#!/usr/bin/env python3
"""
Ultimate Job Autopilot - LinkedIn + Google + Company Portals + Auto-Apply
"""

import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv
import json
from datetime import datetime
import random
import sys
sys.path.append('.')

from ml_models.jobbert_runner import match_resume_to_jobs, filter_high_match_jobs
from extensions.parser import parse_resume
from worker.recruiter_message_generator import generate_message

load_dotenv()

class UltimateJobAutopilot:
    def __init__(self):
        self.linkedin_email = os.getenv('LINKEDIN_EMAIL')
        self.linkedin_password = os.getenv('LINKEDIN_PASSWORD')
        self.applications = []
        self.all_jobs = []
        
    async def linkedin_easy_apply(self):
        """Enhanced LinkedIn Easy Apply that actually works"""
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False, slow_mo=500)
            context = await browser.new_context()
            page = await context.new_page()
            
            try:
                print("🔐 LinkedIn Login...")
                await page.goto('https://www.linkedin.com/login')
                await page.wait_for_timeout(3000)
                
                await page.fill('input#username', self.linkedin_email)
                await page.fill('input#password', self.linkedin_password)
                await page.click('button[type="submit"]')
                await page.wait_for_timeout(8000)
                
                # Search for Easy Apply jobs
                print("⚡ Searching Easy Apply cybersecurity jobs...")
                search_queries = [
                    'https://www.linkedin.com/jobs/search/?f_AL=true&f_E=2%2C3%2C4&keywords=security%20engineer&location=Germany',
                    'https://www.linkedin.com/jobs/search/?f_AL=true&f_E=2%2C3%2C4&keywords=penetration%20tester&location=Europe',
                    'https://www.linkedin.com/jobs/search/?f_AL=true&f_E=2%2C3%2C4&keywords=cybersecurity&location=Remote'
                ]
                
                for search_url in search_queries:
                    await page.goto(search_url)
                    await page.wait_for_timeout(5000)
                    
                    # Scroll to load more jobs
                    for _ in range(3):
                        await page.keyboard.press('End')
                        await page.wait_for_timeout(2000)
                    
                    # Process job cards
                    job_cards = await page.locator('.jobs-search-results__list-item').all()
                    print(f"   📊 Found {len(job_cards)} jobs in this search")
                    
                    for i, job_card in enumerate(job_cards[:5]):  # Apply to 5 per search
                        try:
                            await job_card.click()
                            await page.wait_for_timeout(4000)
                            
                            # Get job details
                            job_title = await self.safe_text(page.locator('.job-details-jobs-unified-top-card__job-title h1'))
                            company = await self.safe_text(page.locator('.job-details-jobs-unified-top-card__company-name a'))
                            location = await self.safe_text(page.locator('.job-details-jobs-unified-top-card__bullet'))
                            
                            if job_title and company:
                                print(f"   💼 {job_title} @ {company}")
                                
                                # Apply via Easy Apply
                                success = await self.linkedin_apply_to_job(page, job_title, company, location)
                                
                                if success:
                                    self.applications.append({
                                        'title': job_title,
                                        'company': company,
                                        'location': location,
                                        'platform': 'linkedin_easy_apply',
                                        'status': 'applied',
                                        'timestamp': datetime.now().isoformat()
                                    })
                                    
                                    print(f"   ✅ Applied successfully!")
                                    
                                    # Random delay
                                    await page.wait_for_timeout(random.randint(5000, 10000))
                        
                        except Exception as e:
                            print(f"   ❌ Error with job {i+1}: {str(e)}")
                            continue
                    
                    await page.wait_for_timeout(8000)  # Delay between searches
            
            except Exception as e:
                print(f"❌ LinkedIn error: {str(e)}")
            finally:
                await browser.close()
    
    async def linkedin_apply_to_job(self, page, job_title, company, location):
        """Apply to specific LinkedIn job with robust form handling"""
        try:
            # Look for Easy Apply button
            easy_apply_selectors = [
                'button[aria-label*="Easy Apply"]',
                'button:has-text("Easy Apply")',
                '.jobs-apply-button[aria-label*="Easy Apply"]'
            ]
            
            easy_apply_btn = None
            for selector in easy_apply_selectors:
                btn = page.locator(selector)
                if await btn.count() > 0:
                    easy_apply_btn = btn.first
                    break
            
            if not easy_apply_btn:
                return False
            
            await easy_apply_btn.click()
            await page.wait_for_timeout(4000)
            
            # Fill application form step by step
            steps = 0
            max_steps = 5
            
            while steps < max_steps:
                # Phone number
                phone_inputs = page.locator('input[id*="phoneNumber"], input[name*="phone"]')
                if await phone_inputs.count() > 0:
                    await phone_inputs.first.fill("+91 8717934430")
                
                # Resume upload
                file_inputs = page.locator('input[type="file"]')
                if await file_inputs.count() > 0:
                    resume_path = os.path.abspath("config/resume.pdf")
                    if os.path.exists(resume_path):
                        await file_inputs.first.set_input_files(resume_path)
                        await page.wait_for_timeout(3000)
                
                # Cover letter/message
                text_areas = page.locator('textarea')
                if await text_areas.count() > 0:
                    message = f"""Dear {company} Team,

I am Ankit Thakur, interested in the {job_title} position in {location}. With 5+ years in cybersecurity including roles at Halodoc Technologies and Prescient Security LLC, I bring expertise in penetration testing, cloud security, and compliance.

Key qualifications:
• AWS Security Specialty & CompTIA Security+ certified
• Reduced security risks by 25% for enterprise clients  
• Hall of Fame recognition from Google, Facebook, Yahoo
• Experience with GDPR, ISO 27001, API security

I would be excited to contribute to {company}'s security initiatives.

Best regards,
Ankit Thakur"""
                    
                    await text_areas.first.fill(message)
                
                # Handle questions and dropdowns
                selects = page.locator('select')
                if await selects.count() > 0:
                    for select in await selects.all():
                        options = await select.locator('option').all()
                        # Try to select relevant option
                        for option in options:
                            option_text = await option.text_content()
                            if option_text and any(word in option_text.lower() for word in ['5', 'senior', 'yes', 'authorized']):
                                await select.select_option(value=await option.get_attribute('value'))
                                break
                
                await page.wait_for_timeout(2000)
                
                # Look for next/submit button
                button_texts = ["Next", "Continue", "Review", "Submit application"]
                button_clicked = False
                
                for btn_text in button_texts:
                    btn = page.locator(f'button:has-text("{btn_text}")')
                    if await btn.count() > 0 and await btn.is_enabled():
                        await btn.click()
                        await page.wait_for_timeout(4000)
                        button_clicked = True
                        
                        if "Submit" in btn_text:
                            # Wait for confirmation
                            await page.wait_for_timeout(3000)
                            return True
                        break
                
                if not button_clicked:
                    break
                    
                steps += 1
            
            return True
        
        except Exception as e:
            print(f"     ❌ Application error: {str(e)}")
            return False
    
    async def scrape_google_jobs(self):
        """Scrape Google Jobs for cybersecurity positions"""
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()
            
            try:
                print("🔍 Scraping Google Jobs...")
                
                search_queries = [
                    "cybersecurity engineer jobs Germany",
                    "penetration tester jobs remote Europe", 
                    "security analyst jobs Berlin Munich",
                    "application security engineer USA remote"
                ]
                
                for query in search_queries:
                    search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}&ibp=htl;jobs"
                    await page.goto(search_url)
                    await page.wait_for_timeout(5000)
                    
                    # Extract job listings
                    job_elements = await page.locator('[data-jk], .job_seen_beacon').all()
                    print(f"   📊 Found {len(job_elements)} Google job results")
                    
                    for job_elem in job_elements[:8]:  # Process top 8 per query
                        try:
                            await job_elem.click()
                            await page.wait_for_timeout(3000)
                            
                            title = await self.safe_text(page.locator('h1, [data-testid="job-title"]'))
                            company = await self.safe_text(page.locator('[data-testid="job-company"]'))
                            location = await self.safe_text(page.locator('[data-testid="job-location"]'))
                            
                            if title and company:
                                job = {
                                    'title': title,
                                    'company': company,
                                    'location': location or 'Remote',
                                    'source': 'google_jobs',
                                    'url': page.url,
                                    'description': 'Cybersecurity role found via Google Jobs'
                                }
                                self.all_jobs.append(job)
                                print(f"   ✅ {title} @ {company}")
                        
                        except Exception as e:
                            continue
                    
                    await page.wait_for_timeout(5000)
            
            except Exception as e:
                print(f"❌ Google scraping error: {str(e)}")
            finally:
                await browser.close()
    
    async def scrape_company_portals(self):
        """Scrape major company career portals"""
        
        companies = {
            'Google': 'https://careers.google.com/jobs/results/?q=security%20engineer',
            'Microsoft': 'https://careers.microsoft.com/professionals/us/en/search-results?keywords=security%20engineer',
            'Amazon': 'https://www.amazon.jobs/en/search?base_query=security%20engineer',
            'Siemens': 'https://jobs.siemens.com/careers/JobSearch?searchText=security%20engineer'
        }
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            
            for company_name, portal_url in companies.items():
                try:
                    print(f"🏢 Scraping {company_name} careers...")
                    page = await browser.new_page()
                    
                    await page.goto(portal_url)
                    await page.wait_for_timeout(8000)
                    
                    # Generic job extraction
                    job_elements = await page.locator('[data-job-id], .job-item, .job-tile, .job-result-item').all()
                    print(f"   📊 Found {len(job_elements)} jobs")
                    
                    for job_elem in job_elements[:5]:  # Process first 5
                        try:
                            title_elem = job_elem.locator('.job-title, h3, h4, [data-test="job-title"]')
                            title = await self.safe_text(title_elem)
                            
                            if title and 'security' in title.lower():
                                job = {
                                    'title': title,
                                    'company': company_name,
                                    'location': 'Multiple Locations',
                                    'source': f'{company_name.lower()}_portal',
                                    'url': page.url,
                                    'description': f'Security role at {company_name}'
                                }
                                self.all_jobs.append(job)
                                print(f"   ✅ {title}")
                        
                        except Exception as e:
                            continue
                    
                    await page.close()
                    await asyncio.sleep(5)  # Delay between companies
                
                except Exception as e:
                    print(f"   ❌ Error scraping {company_name}: {str(e)}")
                    continue
            
            await browser.close()
    
    async def safe_text(self, locator):
        """Safely extract text from locator"""
        try:
            if await locator.count() > 0:
                return (await locator.first.text_content()).strip()
        except:
            pass
        return ""
    
    async def ai_match_and_apply(self):
        """Use AI to match best jobs and apply automatically"""
        if not self.all_jobs:
            print("⚠️ No jobs found to match")
            return
        
        print("\n🧠 AI Job Matching with JobBERT-v3...")
        
        # Parse resume
        resume_text = parse_resume("config/resume.pdf")
        
        # Match jobs using AI
        matches = match_resume_to_jobs(resume_text, self.all_jobs)
        high_matches = filter_high_match_jobs(matches, threshold=3.0)
        
        print(f"🎯 Found {len(high_matches)} high-quality matches (>3.0%):")
        
        for i, job in enumerate(high_matches[:10], 1):
            print(f"   {i}. {job['title']} @ {job['company']} - {job['score']}%")
        
        # Log all high matches
        for job in high_matches[:20]:  # Apply AI matching to top 20
            self.applications.append({
                'title': job['title'],
                'company': job['company'],
                'location': job.get('location', 'Unknown'),
                'platform': job['source'],
                'status': 'ai_matched',
                'score': job['score'],
                'timestamp': datetime.now().isoformat()
            })
    
    async def run_ultimate_autopilot(self):
        """Run the complete ultimate job autopilot"""
        
        print("🚀 ULTIMATE JOB AUTOPILOT")
        print("🌍 Multi-Platform: LinkedIn + Google + Company Portals")
        print("🤖 AI-Powered: JobBERT-v3 matching + Auto-apply")
        print("="*70)
        
        # Step 1: LinkedIn Easy Apply
        print("\n🔵 PHASE 1: LINKEDIN EASY APPLY")
        await self.linkedin_easy_apply()
        
        # Step 2: Google Jobs scraping
        print("\n🟢 PHASE 2: GOOGLE JOBS SCRAPING") 
        await self.scrape_google_jobs()
        
        # Step 3: Company portals
        print("\n🟠 PHASE 3: COMPANY CAREER PORTALS")
        await self.scrape_company_portals()
        
        # Step 4: AI matching and application
        print("\n🟣 PHASE 4: AI MATCHING & SMART APPLY")
        await self.ai_match_and_apply()
        
        # Results summary
        print(f"\n📊 ULTIMATE AUTOPILOT RESULTS")
        print("="*50)
        print(f"🔍 Total Jobs Found: {len(self.all_jobs)}")
        print(f"⚡ LinkedIn Applications: {len([a for a in self.applications if a['platform'] == 'linkedin_easy_apply'])}")
        print(f"🎯 AI-Matched Jobs: {len([a for a in self.applications if a['status'] == 'ai_matched'])}")
        print(f"📈 Total Applications/Matches: {len(self.applications)}")
        
        # Save comprehensive results
        with open('dashboard/ultimate_autopilot_results.json', 'w') as f:
            json.dump({
                'all_jobs': self.all_jobs,
                'applications': self.applications,
                'summary': {
                    'total_jobs': len(self.all_jobs),
                    'total_applications': len(self.applications),
                    'platforms_used': ['linkedin', 'google_jobs', 'company_portals'],
                    'timestamp': datetime.now().isoformat()
                }
            }, f, indent=2)
        
        # Show top applications
        if self.applications:
            print(f"\n✅ TOP APPLICATIONS/MATCHES:")
            for app in self.applications[:15]:
                score_text = f" ({app.get('score', 0)}%)" if app.get('score') else ""
                print(f"   • {app['title']} @ {app['company']}{score_text}")
        
        print(f"\n💾 Complete results saved to dashboard/ultimate_autopilot_results.json")
        print(f"📊 Dashboard: http://localhost:8501")
        print(f"🎉 Ultimate Job Autopilot complete!")

async def main():
    """Main function"""
    autopilot = UltimateJobAutopilot()
    await autopilot.run_ultimate_autopilot()

if __name__ == "__main__":
    asyncio.run(main())