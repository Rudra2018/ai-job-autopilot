import os
import time
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from .application_logger import log_application

load_dotenv()

LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")

XING_EMAIL = os.getenv("XING_EMAIL")
XING_PASSWORD = os.getenv("XING_PASSWORD")

RESUME_PATH = "resumes/resume.pdf"


def simulate_job_apply(job, config=None, recruiter_msg: str | None = None):
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
            page.goto("https://www.linkedin.com/login")
            page.fill("input[name='session_key']", LINKEDIN_EMAIL)
            page.fill("input[name='session_password']", LINKEDIN_PASSWORD)
            page.click("button[type='submit']")
            page.wait_for_url("https://www.linkedin.com/feed*", timeout=10000)

            print(f"🌐 Opening job: {job_url}")
            page.goto(job_url)
            time.sleep(4)

            if page.locator("button:has-text('Easy Apply')").is_visible():
                page.click("button:has-text('Easy Apply')")
                time.sleep(2)

                if page.locator("input[type='file']").is_visible():
                    page.set_input_files("input[type='file']", resume_path)

                # Click through multi-step forms
                while page.locator("button:has-text('Next'), button:has-text('Review'), button:has-text('Submit')").is_visible():
                    try:
                        page.locator("button:has-text('Next'), button:has-text('Review'), button:has-text('Submit')").first.click()
                        time.sleep(2)
                    except:
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
            page.goto("https://login.xing.com/")
            page.fill("input[name='username']", XING_EMAIL)
            page.fill("input[name='password']", XING_PASSWORD)
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


def auto_detect_and_apply(job):
    url = job.get("url", "")
    if "linkedin.com" in url:
        real_linkedin_apply(url)
    elif "xing.com" in url:
        real_xing_apply(url)
    elif "greenhouse.io" in url:
        real_greenhouse_apply(url)
    elif "lever.co" in url:
        real_lever_apply(url)
    else:
        print(f"[⚠️] Unknown platform for job: {url}")
        simulate_job_apply(job)

