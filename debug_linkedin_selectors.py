#!/usr/bin/env python3
"""
Debug LinkedIn Selectors
Inspect the actual HTML structure to find correct selectors
"""

import asyncio
import os
from dotenv import load_dotenv
from src.automation.linkedin_automation import LinkedInCredentials, LinkedInAutomation

async def debug_linkedin_selectors():
    """Debug LinkedIn job card selectors"""
    
    print("🔍 LinkedIn Selector Debug Mode")
    print("=" * 50)
    
    load_dotenv()
    
    email = os.getenv('LINKEDIN_EMAIL')
    password = os.getenv('LINKEDIN_PASSWORD')
    
    if not email or not password:
        print("❌ LinkedIn credentials not found!")
        return False
    
    credentials = LinkedInCredentials(email=email, password=password)
    
    async def progress_callback(update):
        print(f"[{update['timestamp'][11:19]}] {update['message']}")
    
    automation = LinkedInAutomation(credentials, progress_callback)
    
    try:
        # Initialize browser and login
        if not await automation.initialize_browser():
            return False
        
        if not await automation.login_to_linkedin():
            return False
        
        print("\n🔍 Navigating to job search page...")
        search_url = "https://www.linkedin.com/jobs/search/?keywords=cybersecurity%20engineer&location=Remote&f_TPR=r604800&f_LF=f_AL"
        await automation.page.goto(search_url, wait_until='domcontentloaded', timeout=60000)
        await automation.page.wait_for_timeout(5000)
        
        # Scroll to load jobs
        for _ in range(3):
            await automation.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await automation.page.wait_for_timeout(2000)
        
        # Try different job card selectors
        selectors_to_test = [
            '.job-search-card',
            '.jobs-search-results__list-item', 
            '.job-result-card',
            '[data-entity-urn*="jobPosting"]',
            '.scaffold-layout__list-item',
            '.jobs-search__results-list li',
            'li[data-occludable-job-id]',
            '.job-card-container'
        ]
        
        job_cards = []
        working_selector = None
        
        for selector in selectors_to_test:
            cards = await automation.page.query_selector_all(selector)
            print(f"Selector '{selector}': Found {len(cards)} elements")
            if cards and len(cards) > len(job_cards):
                job_cards = cards
                working_selector = selector
        
        if not job_cards:
            print("❌ No job cards found with any selector!")
            return False
        
        print(f"\n✅ Using selector: {working_selector}")
        print(f"📊 Found {len(job_cards)} job cards")
        
        # Inspect first few job cards
        print("\n🔍 Inspecting job card structure...")
        for i, card in enumerate(job_cards[:3]):
            print(f"\n--- Job Card {i+1} ---")
            
            # Get the HTML content of this card
            card_html = await card.inner_html()
            print(f"HTML Preview: {card_html[:200]}...")
            
            # Test different title selectors
            title_selectors = [
                '.base-search-card__title',
                '.job-card__title', 
                'h3 a',
                '.job-title',
                '.entity-result__title',
                'a[data-control-name="job_search_job_title"]',
                '.job-card-container__link',
                '.job-card-container__company-name + div a'
            ]
            
            print("Title selectors:")
            for sel in title_selectors:
                try:
                    elem = await card.query_selector(sel)
                    if elem:
                        text = await elem.text_content()
                        print(f"  ✅ {sel}: '{text[:50]}...'")
                        break
                    else:
                        print(f"  ❌ {sel}: Not found")
                except:
                    print(f"  ❌ {sel}: Error")
            
            # Test different company selectors
            company_selectors = [
                '.base-search-card__subtitle',
                '.job-card__subtitle',
                '.job-result-card__company-name',
                '.entity-result__primary-subtitle',
                'h4 a',
                '.job-card-container__company-name',
                '.job-card-container__company-name a',
                'a[data-control-name="job_search_company_name"]',
                '.job-card-container__metadata-wrapper a',
                '.artdeco-entity-lockup__subtitle',
                'h4'
            ]
            
            print("Company selectors:")
            for sel in company_selectors:
                try:
                    elem = await card.query_selector(sel)
                    if elem:
                        text = await elem.text_content()
                        print(f"  ✅ {sel}: '{text[:50]}...'")
                        break
                    else:
                        print(f"  ❌ {sel}: Not found")
                except:
                    print(f"  ❌ {sel}: Error")
        
        return True
        
    finally:
        await automation.close_browser()

if __name__ == "__main__":
    success = asyncio.run(debug_linkedin_selectors())
    if success:
        print("\n✅ Debug completed successfully!")
    else:
        print("\n❌ Debug failed!")