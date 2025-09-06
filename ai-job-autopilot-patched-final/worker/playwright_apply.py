
import os
import asyncio
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()
EMAIL = os.getenv("JOB_PORTAL_EMAIL")
PASSWORD = os.getenv("JOB_PORTAL_PASSWORD")

async def simulate_job_apply(job):
    print(f"🔁 Attempting to apply to: {job['title']} @ {job['company']}")
    platform = identify_platform(job.get("apply_url", ""))
    if not platform:
        print("[⚠️] Unknown platform for job:", job.get("apply_url", ""))
        return

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            if platform == "linkedin":
                await apply_linkedin(page, job)
            elif platform == "greenhouse":
                await apply_greenhouse(page, job)
            elif platform == "lever":
                await apply_lever(page, job)
            elif platform == "xing":
                await apply_xing(page, job)
            else:
                print("[⚠️] No handler implemented for:", platform)

            await browser.close()

    except Exception as e:
        print("[❌] Playwright error:", str(e))

def identify_platform(url):
    if not url: return None
    url = url.lower()
    if "linkedin.com" in url: return "linkedin"
    if "greenhouse.io" in url: return "greenhouse"
    if "lever.co" in url: return "lever"
    if "xing.com" in url: return "xing"
    return None

async def apply_linkedin(page, job):
    await page.goto("https://www.linkedin.com/login")
    await page.fill("input[name='session_key']", EMAIL)
    await page.fill("input[name='session_password']", PASSWORD)
    await page.click("button[type='submit']")
    await page.wait_for_timeout(2000)
    print(f"[✅] Logged into LinkedIn - skipping actual apply for: {job['title']}")

async def apply_greenhouse(page, job):
    print("[⚙️] Skipping Greenhouse logic – placeholder")

async def apply_lever(page, job):
    print("[⚙️] Skipping Lever logic – placeholder")

async def apply_xing(page, job):
    print("[⚙️] Skipping Xing logic – placeholder")

# CLI test entry
if __name__ == "__main__":
    test_job = {
        "title": "Security Engineer",
        "company": "LinkedIn",
        "apply_url": "https://www.linkedin.com/jobs/view/123456"
    }
    asyncio.run(simulate_job_apply(test_job))
