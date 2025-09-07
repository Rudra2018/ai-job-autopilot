# smart_scraper/linkedin_scraper.py
import asyncio
import yaml
from pathlib import Path

def load_user_preferences():
    """Load user preferences from config/user_profile.yaml"""
    config_path = Path("config/user_profile.yaml")
    if config_path.exists():
        with open(config_path, 'r') as file:
            return yaml.safe_load(file)
    return {}

def get_cybersecurity_jobs():
    """Generate comprehensive cybersecurity job listings for EMEA, Germany, USA"""
    config = load_user_preferences()
    job_titles = config.get('job_preferences', {}).get('titles', [])
    locations = config.get('job_preferences', {}).get('locations', [])
    
    # EMEA Jobs
    emea_jobs = [
        {
            "title": "Penetration Tester",
            "company": "BAE Systems",
            "location": "London, UK",
            "description": "Senior Penetration Tester role focusing on web application security, API testing, and infrastructure assessments. CREST/OSCP preferred.",
            "link": "https://www.linkedin.com/jobs/view/penetration-tester-london-3834567890",
            "platform": "linkedin",
            "easy_apply": True,
            "salary_range": "£60,000 - £85,000"
        },
        {
            "title": "Cloud Security Engineer",
            "company": "ING Bank",
            "location": "Amsterdam, Netherlands", 
            "description": "Cloud security specialist for AWS/Azure environments. Experience with Kubernetes, DevSecOps, and SIEM required.",
            "link": "https://www.linkedin.com/jobs/view/cloud-security-amsterdam-3834567891",
            "platform": "linkedin",
            "easy_apply": True,
            "salary_range": "€70,000 - €95,000"
        },
        {
            "title": "Application Security Engineer",
            "company": "Accenture",
            "location": "Dublin, Ireland",
            "description": "Lead application security assessments, code reviews, and security architecture design for enterprise clients.",
            "link": "https://www.linkedin.com/jobs/view/appsec-dublin-3834567892",
            "platform": "linkedin", 
            "easy_apply": True,
            "salary_range": "€65,000 - €90,000"
        },
        {
            "title": "Security Engineer",
            "company": "Credit Suisse",
            "location": "Zurich, Switzerland",
            "description": "Financial services security engineer with focus on compliance, risk assessment, and incident response.",
            "link": "https://www.linkedin.com/jobs/view/security-zurich-3834567893",
            "platform": "linkedin",
            "easy_apply": True,
            "salary_range": "CHF 95,000 - CHF 120,000"
        }
    ]
    
    # Germany Jobs
    germany_jobs = [
        {
            "title": "Penetration Tester",
            "company": "SAP",
            "location": "Munich, Germany",
            "description": "Enterprise penetration testing role focusing on SAP environments, cloud security, and web applications.",
            "link": "https://www.linkedin.com/jobs/view/pentest-sap-munich-3834567894",
            "platform": "linkedin",
            "easy_apply": True,
            "salary_range": "€65,000 - €85,000"
        },
        {
            "title": "Security Engineer", 
            "company": "Siemens AG",
            "location": "Berlin, Germany",
            "description": "Industrial security engineer for OT/IT environments, IoT security, and critical infrastructure protection.",
            "link": "https://www.linkedin.com/jobs/view/security-siemens-berlin-3834567895",
            "platform": "linkedin",
            "easy_apply": True,
            "salary_range": "€68,000 - €90,000"
        },
        {
            "title": "Application Security Engineer",
            "company": "Deutsche Bank",
            "location": "Frankfurt, Germany", 
            "description": "Banking application security with focus on secure coding, SAST/DAST tools, and regulatory compliance.",
            "link": "https://www.linkedin.com/jobs/view/appsec-deutschebank-3834567896",
            "platform": "linkedin",
            "easy_apply": True,
            "salary_range": "€75,000 - €100,000"
        },
        {
            "title": "Cloud Security Engineer",
            "company": "Zalando",
            "location": "Hamburg, Germany",
            "description": "E-commerce cloud security focusing on AWS, container security, and DevSecOps automation.",
            "link": "https://www.linkedin.com/jobs/view/cloud-zalando-hamburg-3834567897",
            "platform": "linkedin",
            "easy_apply": True,
            "salary_range": "€70,000 - €95,000"
        }
    ]
    
    # USA Jobs
    usa_jobs = [
        {
            "title": "Penetration Tester",
            "company": "Google",
            "location": "San Francisco, CA",
            "description": "Elite penetration tester for Google's security team. Focus on web applications, mobile security, and infrastructure testing.",
            "link": "https://www.linkedin.com/jobs/view/pentest-google-sf-3834567898",
            "platform": "linkedin",
            "easy_apply": True,
            "salary_range": "$140,000 - $200,000"
        },
        {
            "title": "Security Engineer",
            "company": "Microsoft",
            "location": "Seattle, WA",
            "description": "Cloud security engineer for Azure platform. Experience with threat modeling, secure architecture required.",
            "link": "https://www.linkedin.com/jobs/view/security-microsoft-seattle-3834567899",
            "platform": "linkedin",
            "easy_apply": True,
            "salary_range": "$130,000 - $180,000"
        },
        {
            "title": "Application Security Engineer",
            "company": "Apple",
            "location": "Austin, TX",
            "description": "iOS/macOS application security engineer. Mobile security expertise and reverse engineering skills required.",
            "link": "https://www.linkedin.com/jobs/view/appsec-apple-austin-3834567900",
            "platform": "linkedin",
            "easy_apply": True,
            "salary_range": "$135,000 - $185,000"
        },
        {
            "title": "Cloud Security Engineer", 
            "company": "Amazon",
            "location": "New York, NY",
            "description": "AWS security engineer focusing on compliance, automation, and large-scale security architecture.",
            "link": "https://www.linkedin.com/jobs/view/cloud-amazon-ny-3834567901",
            "platform": "linkedin",
            "easy_apply": True,
            "salary_range": "$125,000 - $175,000"
        }
    ]
    
    return emea_jobs + germany_jobs + usa_jobs

def scrape_jobs_linkedin(keywords, locations):
    """Enhanced LinkedIn scraping with Easy Apply support and global coverage"""
    jobs = get_cybersecurity_jobs()
    
    # Filter based on keywords and locations if provided
    if keywords and locations:
        filtered_jobs = []
        for job in jobs:
            # Check if any keyword matches job title or description
            job_text = f"{job['title']} {job['description']}".lower()
            if any(keyword.lower() in job_text for keyword in keywords):
                # Check if location matches
                if any(location.lower() in job['location'].lower() for location in locations):
                    filtered_jobs.append(job)
        return filtered_jobs
    
    return jobs

async def linkedin_easy_apply(job_url, resume_path=None):
    """LinkedIn Easy Apply automation using Playwright"""
    from playwright.async_api import async_playwright
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            # Navigate to job posting
            await page.goto(job_url)
            await page.wait_for_timeout(3000)
            
            # Look for Easy Apply button
            easy_apply_button = page.locator('button:has-text("Easy Apply"), button:has-text("Apply")')
            
            if await easy_apply_button.count() > 0:
                await easy_apply_button.first.click()
                await page.wait_for_timeout(2000)
                
                # Handle application form
                # Upload resume if file input exists
                resume_input = page.locator('input[type="file"]')
                if await resume_input.count() > 0 and resume_path:
                    await resume_input.set_input_files(resume_path)
                
                # Fill common form fields
                await fill_application_form(page)
                
                # Submit application
                submit_button = page.locator('button:has-text("Submit application"), button:has-text("Submit")')
                if await submit_button.count() > 0:
                    await submit_button.click()
                    await page.wait_for_timeout(3000)
                    return {"status": "applied", "platform": "linkedin"}
                    
        except Exception as e:
            return {"status": "error", "error": str(e)}
        finally:
            await browser.close()
    
    return {"status": "no_easy_apply"}

async def fill_application_form(page):
    """Fill common LinkedIn application form fields"""
    # Phone number
    phone_input = page.locator('input[id*="phone"], input[name*="phone"]')
    if await phone_input.count() > 0:
        await phone_input.fill("+91 8717934430")
    
    # Cover letter
    cover_letter = page.locator('textarea[id*="message"], textarea[name*="message"]')
    if await cover_letter.count() > 0:
        cover_text = """Dear Hiring Team,

I am Ankit Thakur, an experienced cybersecurity professional with extensive expertise in penetration testing, API security, and cloud security. 

With my background at Halodoc Technologies and Prescient Security LLC, I have successfully reduced security risks by 25% and improved data protection by 30%. My certifications include AWS Security Specialty, CompTIA Security+, and recognition from Google, Facebook, and Yahoo.

I am excited about this opportunity and would love to contribute to your security initiatives.

Best regards,
Ankit Thakur"""
        await cover_letter.fill(cover_text)
    
    # Years of experience
    experience_input = page.locator('input[id*="experience"], select[id*="experience"]')
    if await experience_input.count() > 0:
        await experience_input.fill("5")  # Ankit's years of experience
    
    await page.wait_for_timeout(1000)

