import os
import time
from typing import Optional, Tuple, Dict

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

from smart_scraper.job_scraper import scrape_jobs_live

from .application_logger import log_application

load_dotenv()

RESUME_PATH = "resumes/resume.pdf"

# Store credentials in-memory so callers can supply them programmatically.
CREDENTIALS: Dict[str, Tuple[str, str]] = {}


def set_platform_credentials(platform: str, email: str, password: str) -> None:
    """Register login credentials for a given platform."""
    CREDENTIALS[platform.lower()] = (email, password)


def _get_platform_credentials(platform: str) -> Tuple[str, str]:
    """Fetch credentials from memory or environment variables."""
    platform = platform.lower()
    if platform in CREDENTIALS:
        return CREDENTIALS[platform]
    return (
        os.getenv(f"{platform.upper()}_EMAIL", ""),
        os.getenv(f"{platform.upper()}_PASSWORD", ""),
    )


def upload_and_parse_resume(resume_path: str = RESUME_PATH) -> Dict:
    """Parse a resume file and return the extracted details."""
    from parser.resume_parser import parse_resume as _parse_resume

    data = _parse_resume(resume_path)
    return data


def smart_apply(
    keywords: Optional[list[str]] = None,
    locations: Optional[list[str]] = None,
    resume_path: str = RESUME_PATH,
) -> None:
    """Use the AI smart scraper to find jobs and auto-apply to them."""
    upload_and_parse_resume(resume_path)
    jobs = scrape_jobs_live(keywords, locations)
    for job in jobs:
        auto_detect_and_apply(job, resume_path)


def simulate_job_apply(job, config=None, recruiter_msg: Optional[str] = None):
    """Light-weight stand in for the full Playwright automation.

    The real project drives a headless browser to apply for jobs.  For the
    purposes of the tests and offline execution we simply log what would have
    happened.  The ``config`` and ``recruiter_msg`` parameters are accepted for
    API-compatibility with the rest of the codebase but are optional.
    """

    print(f"[✅] Simulated applying to job: {job['title']} at {job['company']}")
    if recruiter_msg:
        print(f"    ↳ recruiter message: {recruiter_msg}")
    log_application(job, "simulated", recruiter_msg=recruiter_msg)


def real_linkedin_apply(job_url, resume_path=RESUME_PATH):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        try:
            print("🔐 Logging into LinkedIn...")
            email, password = _get_platform_credentials("linkedin")
            page.goto("https://www.linkedin.com/login")
            page.fill("input[name='session_key']", email)
            page.fill("input[name='session_password']", password)
            page.click("button[type='submit']")
            page.wait_for_url("https://www.linkedin.com/feed*", timeout=10000)

            print(f"🌐 Opening job: {job_url}")
            page.goto(job_url)
            # Wait for the job page to fully load before searching for buttons
            page.wait_for_load_state("domcontentloaded")

            # Look for the Easy Apply button using multiple selectors to handle UI changes
            easy_apply_selectors = [
                "button:has-text('Easy Apply')",
                "button:has-text('Apply')",
                "button[aria-label*='Easy Apply']",
                ".jobs-apply-button--top-card",
            ]

            easy_apply_button = None
            for selector in easy_apply_selectors:
                locator = page.locator(selector).first
                try:
                    locator.wait_for(state="visible", timeout=3000)
                    easy_apply_button = locator
                    break
                except PlaywrightTimeout:
                    continue

            if easy_apply_button:
                easy_apply_button.click()
                page.wait_for_timeout(1000)

                if page.locator("input[type='file']").is_visible():
                    page.set_input_files("input[type='file']", resume_path)

                # Click through multi-step forms
                while True:
                    next_button = page.locator(
                        "button:has-text('Next'), button:has-text('Review'), button:has-text('Submit')"
                    ).first
                    if not next_button.is_visible():
                        break
                    try:
                        next_button.click()
                        page.wait_for_timeout(1000)
                    except Exception:
                        break

                print(f"[✅] Applied to LinkedIn job: {job_url}")
            else:
                print(f"[⚠️] No 'Easy Apply' found on LinkedIn job: {job_url}")

        except PlaywrightTimeout:
            print("⏱️ Login or job page load timed out!")
        finally:
            browser.close()


def real_xing_apply(job_url, resume_path=RESUME_PATH):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        try:
            print("🔐 Logging into Xing...")
            email, password = _get_platform_credentials("xing")
            page.goto("https://login.xing.com/")
            page.fill("input[name='username']", email)
            page.fill("input[name='password']", password)
            page.click("button[type='submit']")
            page.wait_for_url("https://www.xing.com/feed", timeout=10000)

            print(f"🌐 Opening job: {job_url}")
            page.goto(job_url)
            time.sleep(3)

            # Add Xing-specific apply logic here
            print("[⚠️] Xing apply flow needs manual implementation (form parsing differs per job).")

        except Exception as e:
            print(f"[❌] Xing apply failed: {e}")
        finally:
            browser.close()


def real_greenhouse_apply(job_url, resume_path=RESUME_PATH):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        try:
            print(f"🌐 Opening Greenhouse job: {job_url}")
            page.goto(job_url)
            time.sleep(2)

            if page.locator("input[type='file']").is_visible():
                page.set_input_files("input[type='file']", resume_path)
                print("[✅] Resume uploaded to Greenhouse form")
            else:
                print("[⚠️] Resume upload field not found")

        except Exception as e:
            print(f"[❌] Greenhouse apply failed: {e}")
        finally:
            browser.close()


def real_lever_apply(job_url, resume_path=RESUME_PATH):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        try:
            print(f"🌐 Opening Lever job: {job_url}")
            page.goto(job_url)
            time.sleep(2)

            if page.locator("input[type='file']").is_visible():
                page.set_input_files("input[type='file']", resume_path)
                print("[✅] Resume uploaded to Lever form")
            else:
                print("[⚠️] Resume upload field not found")

        except Exception as e:
            print(f"[❌] Lever apply failed: {e}")
        finally:
            browser.close()


def auto_detect_and_apply(job, resume_path: str = RESUME_PATH):
    url = job.get("url", "")
    if "linkedin.com" in url:
        real_linkedin_apply(url, resume_path)
    elif "xing.com" in url:
        real_xing_apply(url, resume_path)
    elif "greenhouse.io" in url:
        real_greenhouse_apply(url, resume_path)
    elif "lever.co" in url:
        real_lever_apply(url, resume_path)
    else:
        print(f"[⚠️] Unknown platform for job: {url}")
        simulate_job_apply(job)

