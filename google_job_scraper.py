#!/usr/bin/env python3
"""
Google Jobs Scraper with Automatic Application
"""

import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv
import json
from datetime import datetime
import re
from urllib.parse import urlparse

load_dotenv()

async def scrape_google_jobs():
    """Scrape cybersecurity jobs from Google Jobs"""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        jobs = []
        
        try:
            # Search queries for different regions and roles
            search_queries = [
                "cybersecurity jobs Germany",
                "security engineer jobs Berlin Munich", 
                "penetration tester jobs Europe",
                "application security engineer remote",
                "cloud security engineer USA",
                "information security analyst London"
            ]
            
            for query in search_queries:
                print(f"\n🔍 Searching Google Jobs: {query}")
                
                # Google Jobs search
                search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}&ibp=htl;jobs"
                await page.goto(search_url)
                await page.wait_for_timeout(5000)
                
                # Handle Google's cookie consent if present
                try:
                    accept_btn = page.locator('button:has-text("Accept all"), button:has-text("I agree")')
                    if await accept_btn.count() > 0:
                        await accept_btn.first.click()
                        await page.wait_for_timeout(2000)
                except:
                    pass
                
                # Find job cards
                job_cards = await page.locator('[data-jk], .job_seen_beacon, [data-job-id]').all()
                print(f"📊 Found {len(job_cards)} job listings")
                
                for i, job_card in enumerate(job_cards[:10]):  # Process first 10 per query
                    try:
                        await job_card.click()
                        await page.wait_for_timeout(3000)
                        
                        # Extract job details
                        title_elem = page.locator('h1, .jobsearch-JobInfoHeader-title, [data-testid="job-title"]')
                        company_elem = page.locator('[data-testid="job-company"], .jobsearch-CompanyReview--link')
                        location_elem = page.locator('[data-testid="job-location"], .jobsearch-JobMetadataHeader-item')
                        description_elem = page.locator('[data-testid="job-description"], .jobsearch-jobDescriptionText')
                        
                        title = await get_text_content(title_elem)
                        company = await get_text_content(company_elem)
                        location = await get_text_content(location_elem)
                        description = await get_text_content(description_elem)
                        
                        if title and company:
                            job = {
                                'title': title,
                                'company': company,
                                'location': location or 'Remote',
                                'description': description[:500] if description else '',
                                'source': 'google_jobs',
                                'url': page.url,
                                'scraped_at': datetime.now().isoformat()
                            }
                            jobs.append(job)
                            print(f"   ✅ {title} @ {company}")
                        
                    except Exception as e:
                        print(f"   ❌ Error extracting job {i+1}: {str(e)}")
                        continue
                
                await page.wait_for_timeout(3000)
            
        except Exception as e:
            print(f"❌ Error scraping Google Jobs: {str(e)}")
        finally:
            await browser.close()
    
    return jobs

async def get_text_content(locator):
    """Safely get text content from locator"""
    try:
        if await locator.count() > 0:
            return (await locator.first.text_content()).strip()
    except:
        pass
    return ""

async def main():
    """Main Google Jobs scraper"""
    print("🔍 GOOGLE JOBS SCRAPER")
    print("🎯 Target: Cybersecurity roles globally")
    print("="*50)
    
    jobs = await scrape_google_jobs()
    
    print(f"\n📊 SCRAPING RESULTS")
    print("="*30)
    print(f"✅ Jobs Found: {len(jobs)}")
    
    if jobs:
        # Save to file
        with open('dashboard/google_jobs.json', 'w') as f:
            json.dump(jobs, f, indent=2)
        
        # Show sample jobs
        print(f"\n🎯 SAMPLE JOBS:")
        for job in jobs[:5]:
            print(f"   • {job['title']} @ {job['company']} ({job['location']})")
        
        print(f"\n💾 Results saved to dashboard/google_jobs.json")
    
    return jobs

if __name__ == "__main__":
    asyncio.run(main())