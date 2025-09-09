#!/usr/bin/env python3
"""
🤖 AI Job Autopilot - Undetected Browser Automation
Advanced stealth browser automation with human-like behavior patterns
"""

import os
import time
import random
import logging
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import json
from datetime import datetime
from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class BrowserConfig:
    headless: bool = False
    user_agent: str = ""
    viewport_width: int = 1920
    viewport_height: int = 1080
    locale: str = "en-US"
    timezone: str = "America/New_York"
    geolocation: Dict = None
    proxy: Dict = None
    stealth_mode: bool = True

@dataclass
class HumanBehaviorConfig:
    typing_delay_range: Tuple[int, int] = (50, 200)  # milliseconds
    click_delay_range: Tuple[int, int] = (100, 500)
    scroll_delay_range: Tuple[int, int] = (200, 800)
    page_load_wait_range: Tuple[int, int] = (2, 5)  # seconds
    mouse_movement_steps: int = 10
    natural_pauses: bool = True
    random_scrolling: bool = True

class UndetectedBrowser:
    def __init__(self, 
                 browser_config: BrowserConfig = None,
                 behavior_config: HumanBehaviorConfig = None,
                 profile_dir: str = "data/browser_profiles"):
        
        self.browser_config = browser_config or BrowserConfig()
        self.behavior_config = behavior_config or HumanBehaviorConfig()
        self.profile_dir = Path(profile_dir)
        self.profile_dir.mkdir(exist_ok=True)
        
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        
        # User agents for rotation
        self.user_agents = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0"
        ]
        
        # Common screen resolutions
        self.screen_resolutions = [
            (1920, 1080), (1366, 768), (1536, 864), (1440, 900),
            (1280, 720), (1600, 900), (1920, 1200), (2560, 1440)
        ]
    
    def start_browser(self, profile_name: str = "default") -> bool:
        """Start the undetected browser with stealth configurations"""
        try:
            self.playwright = sync_playwright().start()
            
            # Select random user agent if not specified
            if not self.browser_config.user_agent:
                self.browser_config.user_agent = random.choice(self.user_agents)
            
            # Select random screen resolution
            width, height = random.choice(self.screen_resolutions)
            self.browser_config.viewport_width = width
            self.browser_config.viewport_height = height
            
            # Browser launch arguments for stealth
            launch_args = [
                '--no-first-run',
                '--no-default-browser-check',
                '--disable-blink-features=AutomationControlled',
                '--disable-features=VizDisplayCompositor',
                '--disable-background-networking',
                '--disable-background-timer-throttling',
                '--disable-renderer-backgrounding',
                '--disable-backgrounding-occluded-windows',
                '--disable-client-side-phishing-detection',
                '--disable-sync',
                '--metrics-recording-only',
                '--no-report-upload',
                '--disable-dev-shm-usage',
                '--disable-extensions-except=/path/to/ublock',
                '--load-extension=/path/to/ublock',
            ]
            
            # Launch browser
            self.browser = self.playwright.chromium.launch(
                headless=self.browser_config.headless,
                args=launch_args,
                slow_mo=50  # Add slight delay between actions
            )
            
            # Create context with stealth settings
            context_options = {
                'viewport': {
                    'width': self.browser_config.viewport_width, 
                    'height': self.browser_config.viewport_height
                },
                'user_agent': self.browser_config.user_agent,
                'locale': self.browser_config.locale,
                'timezone_id': self.browser_config.timezone,
                'permissions': ['geolocation', 'notifications'],
                'java_script_enabled': True,
                'accept_downloads': True
            }
            
            # Add geolocation if specified
            if self.browser_config.geolocation:
                context_options['geolocation'] = self.browser_config.geolocation
            
            # Add proxy if specified
            if self.browser_config.proxy:
                context_options['proxy'] = self.browser_config.proxy
            
            # Use persistent context for profiles
            profile_path = self.profile_dir / profile_name
            if profile_path.exists():
                self.context = self.browser.new_context(
                    storage_state=str(profile_path / "state.json"),
                    **context_options
                )
            else:
                profile_path.mkdir(exist_ok=True)
                self.context = self.browser.new_context(**context_options)
            
            # Apply stealth scripts
            if self.browser_config.stealth_mode:
                self._apply_stealth_scripts()
            
            # Create new page
            self.page = self.context.new_page()
            
            # Set additional headers
            self._set_realistic_headers()
            
            logger.info(f"Browser started successfully with profile: {profile_name}")
            logger.info(f"User Agent: {self.browser_config.user_agent}")
            logger.info(f"Viewport: {width}x{height}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error starting browser: {e}")
            return False
    
    def _apply_stealth_scripts(self):
        """Apply JavaScript stealth scripts to avoid detection"""
        stealth_scripts = [
            # Override webdriver property
            """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            """,
            
            # Override chrome runtime
            """
            window.chrome = {
                runtime: {}
            };
            """,
            
            # Override plugins
            """
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
            """,
            
            # Override languages
            """
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en'],
            });
            """,
            
            # Override permissions
            """
            const originalQuery = window.navigator.permissions.query;
            return originalQuery.apply(this, arguments).then((result) => {
                if (result.name === 'notifications') {
                    return {...result, state: Notification.permission};
                }
                return result;
            });
            """,
            
            # Mock battery API
            """
            if ('getBattery' in navigator) {
                navigator.getBattery = () => Promise.resolve({
                    charging: true,
                    chargingTime: 0,
                    dischargingTime: Infinity,
                    level: 1
                });
            }
            """
        ]
        
        # Apply stealth scripts to context
        for script in stealth_scripts:
            try:
                self.context.add_init_script(script)
            except Exception as e:
                logger.warning(f"Failed to apply stealth script: {e}")
    
    def _set_realistic_headers(self):
        """Set realistic HTTP headers"""
        realistic_headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1'
        }
        
        self.context.set_extra_http_headers(realistic_headers)
    
    def human_type(self, selector: str, text: str, clear_first: bool = True):
        """Type text with human-like delays"""
        if not self.page:
            raise Exception("Browser not started")
        
        element = self.page.wait_for_selector(selector, timeout=10000)
        if not element:
            raise Exception(f"Element not found: {selector}")
        
        # Clear existing text if requested
        if clear_first:
            element.click()
            self.page.keyboard.press("Control+a")
            time.sleep(0.1)
        
        # Type with random delays
        for char in text:
            element.type(char)
            delay = random.randint(*self.behavior_config.typing_delay_range) / 1000
            time.sleep(delay)
        
        # Random pause after typing
        if self.behavior_config.natural_pauses:
            pause = random.uniform(0.2, 0.8)
            time.sleep(pause)
    
    def human_click(self, selector: str, timeout: int = 10000):
        """Click with human-like behavior"""
        if not self.page:
            raise Exception("Browser not started")
        
        element = self.page.wait_for_selector(selector, timeout=timeout)
        if not element:
            raise Exception(f"Element not found: {selector}")
        
        # Get element position for natural mouse movement
        box = element.bounding_box()
        if box:
            # Click at a random point within the element
            x = box['x'] + random.uniform(0.2, 0.8) * box['width']
            y = box['y'] + random.uniform(0.2, 0.8) * box['height']
            
            # Move mouse to position with steps
            self.page.mouse.move(x, y, steps=self.behavior_config.mouse_movement_steps)
            
            # Random delay before click
            delay = random.randint(*self.behavior_config.click_delay_range) / 1000
            time.sleep(delay)
            
            # Click
            self.page.mouse.click(x, y)
        else:
            # Fallback to normal click
            element.click()
        
        # Random pause after clicking
        if self.behavior_config.natural_pauses:
            pause = random.uniform(0.1, 0.5)
            time.sleep(pause)
    
    def human_scroll(self, direction: str = "down", amount: int = None):
        """Scroll with human-like behavior"""
        if not self.page:
            raise Exception("Browser not started")
        
        if amount is None:
            amount = random.randint(200, 600)
        
        if direction == "down":
            delta_y = amount
        elif direction == "up":
            delta_y = -amount
        else:
            delta_y = amount
        
        # Scroll in steps
        steps = random.randint(3, 8)
        step_amount = delta_y / steps
        
        for _ in range(steps):
            self.page.mouse.wheel(0, step_amount)
            delay = random.randint(*self.behavior_config.scroll_delay_range) / 1000
            time.sleep(delay)
    
    def random_mouse_movement(self):
        """Make random mouse movements to appear more human"""
        if not self.page:
            return
        
        try:
            viewport = self.page.viewport_size
            if viewport:
                x = random.randint(100, viewport['width'] - 100)
                y = random.randint(100, viewport['height'] - 100)
                self.page.mouse.move(x, y, steps=random.randint(5, 15))
        except Exception as e:
            logger.warning(f"Random mouse movement failed: {e}")
    
    def random_scroll_behavior(self):
        """Perform random scrolling to mimic human behavior"""
        if not self.behavior_config.random_scrolling:
            return
        
        try:
            # Random scroll direction and amount
            direction = random.choice(["down", "up"])
            amount = random.randint(100, 400)
            
            self.human_scroll(direction, amount)
            
            # Sometimes scroll back
            if random.random() < 0.3:
                opposite = "up" if direction == "down" else "down"
                self.human_scroll(opposite, amount // 2)
                
        except Exception as e:
            logger.warning(f"Random scroll behavior failed: {e}")
    
    def wait_for_page_load(self, timeout: int = 30000):
        """Wait for page to load with random delay"""
        if not self.page:
            raise Exception("Browser not started")
        
        # Wait for network to be idle
        self.page.wait_for_load_state("networkidle", timeout=timeout)
        
        # Additional random delay
        delay = random.uniform(*self.behavior_config.page_load_wait_range)
        time.sleep(delay)
        
        # Random behavior after page load
        if random.random() < 0.3:
            self.random_mouse_movement()
        
        if random.random() < 0.2:
            self.random_scroll_behavior()
    
    def navigate_to(self, url: str, wait_for_load: bool = True):
        """Navigate to URL with human-like behavior"""
        if not self.page:
            raise Exception("Browser not started")
        
        logger.info(f"Navigating to: {url}")
        
        # Navigate
        self.page.goto(url, wait_until="domcontentloaded")
        
        if wait_for_load:
            self.wait_for_page_load()
    
    def save_profile(self, profile_name: str = "default"):
        """Save browser profile state"""
        if not self.context:
            return
        
        try:
            profile_path = self.profile_dir / profile_name
            profile_path.mkdir(exist_ok=True)
            
            # Save storage state
            storage_state = self.context.storage_state()
            with open(profile_path / "state.json", "w") as f:
                json.dump(storage_state, f, indent=2)
            
            logger.info(f"Profile saved: {profile_name}")
            
        except Exception as e:
            logger.error(f"Error saving profile: {e}")
    
    def take_screenshot(self, filename: str = None) -> str:
        """Take screenshot with timestamp"""
        if not self.page:
            raise Exception("Browser not started")
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
        
        screenshot_path = Path("data/screenshots") / filename
        screenshot_path.parent.mkdir(exist_ok=True)
        
        self.page.screenshot(path=str(screenshot_path), full_page=True)
        logger.info(f"Screenshot saved: {screenshot_path}")
        
        return str(screenshot_path)
    
    def close(self, save_profile_name: str = None):
        """Close browser and optionally save profile"""
        if save_profile_name:
            self.save_profile(save_profile_name)
        
        if self.context:
            self.context.close()
        
        if self.browser:
            self.browser.close()
        
        if self.playwright:
            self.playwright.stop()
        
        logger.info("Browser closed successfully")
    
    def get_current_url(self) -> str:
        """Get current page URL"""
        if not self.page:
            return ""
        return self.page.url
    
    def get_page_title(self) -> str:
        """Get current page title"""
        if not self.page:
            return ""
        return self.page.title()
    
    def is_element_visible(self, selector: str) -> bool:
        """Check if element is visible on page"""
        if not self.page:
            return False
        
        try:
            element = self.page.query_selector(selector)
            return element.is_visible() if element else False
        except:
            return False
    
    def wait_for_selector(self, selector: str, timeout: int = 10000):
        """Wait for selector with timeout"""
        if not self.page:
            raise Exception("Browser not started")
        
        return self.page.wait_for_selector(selector, timeout=timeout)
    
    def execute_script(self, script: str):
        """Execute JavaScript in the page"""
        if not self.page:
            raise Exception("Browser not started")
        
        return self.page.evaluate(script)
    
    def get_text(self, selector: str) -> str:
        """Get text content of element"""
        if not self.page:
            return ""
        
        try:
            element = self.page.query_selector(selector)
            return element.text_content() if element else ""
        except:
            return ""


def main():
    """Demo the Undetected Browser"""
    print("🤖 Undetected Browser Demo")
    print("=" * 50)
    
    # Configure browser for stealth
    browser_config = BrowserConfig(
        headless=False,  # Set to True for production
        stealth_mode=True
    )
    
    # Configure human-like behavior
    behavior_config = HumanBehaviorConfig(
        typing_delay_range=(80, 150),
        click_delay_range=(200, 400),
        natural_pauses=True,
        random_scrolling=True
    )
    
    # Initialize browser
    browser = UndetectedBrowser(browser_config, behavior_config)
    
    try:
        # Start browser
        print("\\n🚀 Starting undetected browser...")
        success = browser.start_browser("demo_profile")
        
        if not success:
            print("❌ Failed to start browser")
            return
        
        print("✅ Browser started successfully")
        
        # Navigate to a test site
        print("\\n🌐 Navigating to test site...")
        browser.navigate_to("https://bot.sannysoft.com/")
        
        # Take screenshot
        print("\\n📸 Taking screenshot...")
        screenshot_path = browser.take_screenshot()
        print(f"Screenshot saved: {screenshot_path}")
        
        # Demonstrate human-like behavior
        print("\\n🤖 Demonstrating human-like behavior...")
        
        # Random scrolling
        browser.human_scroll("down", 300)
        time.sleep(1)
        browser.human_scroll("up", 150)
        
        # Random mouse movements
        browser.random_mouse_movement()
        time.sleep(0.5)
        browser.random_mouse_movement()
        
        # Wait a bit
        time.sleep(2)
        
        print("\\n✅ Demo completed successfully")
        
        # Show current page info
        print(f"\\n📄 Current Page:")
        print(f"   URL: {browser.get_current_url()}")
        print(f"   Title: {browser.get_page_title()}")
        
    except Exception as e:
        print(f"❌ Demo error: {e}")
        logger.error(f"Demo error: {e}")
    
    finally:
        # Close browser
        print("\\n🔒 Closing browser...")
        browser.close("demo_profile")
        print("✅ Browser closed and profile saved")


if __name__ == "__main__":
    main()