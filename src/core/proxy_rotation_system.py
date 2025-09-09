#!/usr/bin/env python3
"""
Proxy Rotation and Anti-Detection System
Advanced system for rotating proxies and avoiding detection during scraping
"""

import asyncio
import json
import os
import random
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import aiohttp
import requests
from playwright.async_api import Browser, BrowserContext, Page
import yaml

@dataclass
class ProxyConfig:
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    protocol: str = 'http'  # http, https, socks5
    country: Optional[str] = None
    speed_score: float = 0.0
    success_rate: float = 1.0
    last_used: Optional[str] = None
    is_working: bool = True

@dataclass
class DetectionMetrics:
    request_count: int = 0
    blocked_count: int = 0
    captcha_count: int = 0
    success_count: int = 0
    last_detection: Optional[str] = None
    detection_score: float = 0.0  # Higher = more likely to be detected

class ProxyRotationSystem:
    """Advanced proxy rotation system with health monitoring"""
    
    def __init__(self, config_path: str = "config/proxy_config.yaml"):
        # Setup logging first
        self.logger = logging.getLogger(__name__)
        
        self.config = self._load_config(config_path)
        self.proxies: List[ProxyConfig] = []
        self.current_proxy_index = 0
        self.proxy_health_stats = {}
        self.detection_metrics = DetectionMetrics()
        
        # User agent rotation
        self.user_agents = self._load_user_agents()
        self.current_ua_index = 0
        
        # Browser fingerprinting evasion
        self.fingerprints = self._load_browser_fingerprints()
        
        # Rate limiting
        self.request_history = []
        self.blocked_domains = set()
        
        # Initialize proxies
        self._initialize_proxies()
    
    def _load_config(self, config_path: str) -> Dict:
        """Load proxy configuration"""
        try:
            with open(config_path) as f:
                config = yaml.safe_load(f)
            return config
        except FileNotFoundError:
            self.logger.warning(f"Proxy config not found: {config_path}, using defaults")
            return self._get_default_proxy_config()
    
    def _get_default_proxy_config(self) -> Dict:
        """Get default proxy configuration"""
        return {
            'enabled': False,  # Disabled by default for safety
            'rotation_strategy': 'round_robin',  # round_robin, random, health_based
            'health_check_interval': 300,  # seconds
            'max_requests_per_proxy': 100,
            'retry_attempts': 3,
            'timeout': 30,
            'proxy_sources': {
                'free_proxies': False,
                'premium_proxies': False,
                'residential_proxies': False
            },
            'detection_evasion': {
                'rotate_user_agents': True,
                'randomize_headers': True,
                'vary_timing': True,
                'simulate_human_behavior': True
            },
            'rate_limiting': {
                'enabled': True,
                'requests_per_minute': 60,
                'burst_limit': 10
            }
        }
    
    def _initialize_proxies(self):
        """Initialize proxy list from various sources"""
        if not self.config.get('enabled', False):
            self.logger.info("Proxy rotation disabled in config")
            return
        
        self.logger.info("🔄 Initializing proxy rotation system...")
        
        # Load proxy sources
        if self.config['proxy_sources'].get('premium_proxies'):
            self._load_premium_proxies()
        
        if self.config['proxy_sources'].get('free_proxies'):
            self._load_free_proxies()
        
        if self.config['proxy_sources'].get('residential_proxies'):
            self._load_residential_proxies()
        
        # If no proxies loaded, disable proxy rotation
        if not self.proxies:
            self.logger.warning("No proxies available, disabling proxy rotation")
            self.config['enabled'] = False
        else:
            self.logger.info(f"✅ Loaded {len(self.proxies)} proxies")
            # Start health monitoring
            asyncio.create_task(self._monitor_proxy_health())
    
    def _load_premium_proxies(self):
        """Load premium proxy services (implement with your proxy provider)"""
        # Example premium proxy services: Bright Data, Smartproxy, Oxylabs
        premium_proxies = [
            # Example format - replace with real proxy data
            ProxyConfig(
                host="premium-proxy-1.example.com",
                port=8080,
                username="your_username",
                password="your_password",
                protocol="http",
                country="US"
            )
        ]
        
        self.proxies.extend(premium_proxies)
        self.logger.info(f"Loaded {len(premium_proxies)} premium proxies")
    
    def _load_free_proxies(self):
        """Load and validate free proxies"""
        try:
            # Example free proxy sources
            free_proxy_apis = [
                "https://api.proxyscrape.com/v2/?request=get&protocol=http&timeout=10000&country=all",
                "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt"
            ]
            
            for api_url in free_proxy_apis:
                try:
                    response = requests.get(api_url, timeout=10)
                    if response.status_code == 200:
                        proxy_list = response.text.strip().split('\n')
                        for proxy_str in proxy_list[:20]:  # Limit to 20 free proxies
                            if ':' in proxy_str:
                                host, port = proxy_str.strip().split(':')
                                proxy = ProxyConfig(
                                    host=host,
                                    port=int(port),
                                    protocol='http'
                                )
                                self.proxies.append(proxy)
                except Exception as e:
                    self.logger.warning(f"Failed to load from {api_url}: {e}")
            
            self.logger.info(f"Loaded free proxies (validation needed)")
            
        except Exception as e:
            self.logger.error(f"Error loading free proxies: {e}")
    
    def _load_residential_proxies(self):
        """Load residential proxy services"""
        # Example residential proxy providers
        # These typically require API integration
        self.logger.info("Residential proxy loading not implemented")
    
    def _load_user_agents(self) -> List[str]:
        """Load realistic user agent strings"""
        return [
            # Chrome on Windows
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            
            # Chrome on macOS
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            
            # Firefox on Windows
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:119.0) Gecko/20100101 Firefox/119.0",
            
            # Firefox on macOS
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0",
            
            # Safari on macOS
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
            
            # Edge on Windows
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
        ]
    
    def _load_browser_fingerprints(self) -> List[Dict]:
        """Load browser fingerprint configurations"""
        return [
            {
                'viewport': {'width': 1920, 'height': 1080},
                'screen': {'width': 1920, 'height': 1080},
                'timezone': 'America/New_York',
                'language': 'en-US,en;q=0.9'
            },
            {
                'viewport': {'width': 1440, 'height': 900},
                'screen': {'width': 1440, 'height': 900},
                'timezone': 'America/Los_Angeles',
                'language': 'en-US,en;q=0.9'
            },
            {
                'viewport': {'width': 1366, 'height': 768},
                'screen': {'width': 1366, 'height': 768},
                'timezone': 'Europe/London',
                'language': 'en-GB,en;q=0.9'
            },
            {
                'viewport': {'width': 1536, 'height': 864},
                'screen': {'width': 1536, 'height': 864},
                'timezone': 'Europe/Berlin',
                'language': 'en-US,en;q=0.9,de;q=0.8'
            }
        ]
    
    async def get_next_proxy(self) -> Optional[ProxyConfig]:
        """Get the next proxy based on rotation strategy"""
        if not self.config.get('enabled') or not self.proxies:
            return None
        
        # Filter working proxies
        working_proxies = [p for p in self.proxies if p.is_working]
        
        if not working_proxies:
            self.logger.warning("No working proxies available")
            return None
        
        strategy = self.config.get('rotation_strategy', 'round_robin')
        
        if strategy == 'round_robin':
            proxy = working_proxies[self.current_proxy_index % len(working_proxies)]
            self.current_proxy_index += 1
            
        elif strategy == 'random':
            proxy = random.choice(working_proxies)
            
        elif strategy == 'health_based':
            # Sort by success rate and speed
            sorted_proxies = sorted(working_proxies, 
                                  key=lambda p: (p.success_rate, -p.speed_score), 
                                  reverse=True)
            proxy = sorted_proxies[0]
            
        else:
            proxy = working_proxies[0]
        
        # Update usage tracking
        proxy.last_used = datetime.now().isoformat()
        
        return proxy
    
    async def create_proxy_context(self, browser: Browser) -> BrowserContext:
        """Create browser context with proxy and anti-detection measures"""
        
        # Get proxy
        proxy = await self.get_next_proxy()
        
        # Get fingerprint
        fingerprint = random.choice(self.fingerprints)
        
        # Get user agent
        user_agent = self.user_agents[self.current_ua_index % len(self.user_agents)]
        self.current_ua_index += 1
        
        # Create context options
        context_options = {
            'user_agent': user_agent,
            'viewport': fingerprint['viewport'],
            'screen': fingerprint['screen'],
            'timezone_id': fingerprint['timezone'],
            'locale': fingerprint['language'].split(',')[0],
            'extra_http_headers': self._generate_realistic_headers()
        }
        
        # Add proxy if available
        if proxy:
            proxy_config = {
                'server': f"{proxy.protocol}://{proxy.host}:{proxy.port}"
            }
            
            if proxy.username and proxy.password:
                proxy_config['username'] = proxy.username
                proxy_config['password'] = proxy.password
            
            context_options['proxy'] = proxy_config
            self.logger.info(f"🔄 Using proxy: {proxy.host}:{proxy.port}")
        
        # Create context
        context = await browser.new_context(**context_options)
        
        # Add additional anti-detection measures
        await self._apply_stealth_measures(context)
        
        return context
    
    def _generate_realistic_headers(self) -> Dict[str, str]:
        """Generate realistic HTTP headers"""
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': random.choice([
                'en-US,en;q=0.9',
                'en-GB,en;q=0.9',
                'en-US,en;q=0.9,de;q=0.8',
                'en-US,en;q=0.9,es;q=0.8'
            ]),
            'Cache-Control': 'max-age=0',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1'
        }
        
        # Randomly add optional headers
        if random.random() > 0.5:
            headers['DNT'] = '1'
        
        return headers
    
    async def _apply_stealth_measures(self, context: BrowserContext):
        """Apply stealth measures to avoid detection"""
        
        # Override navigator properties
        await context.add_init_script("""
            // Override webdriver property
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            
            // Override plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [
                    {
                        0: {type: "application/x-google-chrome-pdf", suffixes: "pdf", description: "Portable Document Format"},
                        description: "Portable Document Format",
                        filename: "internal-pdf-viewer",
                        length: 1,
                        name: "Chrome PDF Plugin"
                    },
                    {
                        0: {type: "application/pdf", suffixes: "pdf", description: ""},
                        description: "",
                        filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai",
                        length: 1,
                        name: "Chrome PDF Viewer"
                    }
                ],
            });
            
            // Override languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en'],
            });
            
            // Override permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
            
            // Override chrome runtime
            window.chrome = {
                runtime: {},
            };
        """)
    
    async def _monitor_proxy_health(self):
        """Monitor proxy health and update statistics"""
        while True:
            if not self.config.get('enabled'):
                await asyncio.sleep(60)
                continue
            
            try:
                self.logger.info("🔍 Checking proxy health...")
                
                for proxy in self.proxies:
                    try:
                        # Test proxy with a simple request
                        is_working = await self._test_proxy(proxy)
                        proxy.is_working = is_working
                        
                        # Update statistics
                        if proxy.host not in self.proxy_health_stats:
                            self.proxy_health_stats[proxy.host] = {
                                'total_requests': 0,
                                'successful_requests': 0,
                                'last_check': datetime.now().isoformat()
                            }
                        
                        stats = self.proxy_health_stats[proxy.host]
                        stats['total_requests'] += 1
                        
                        if is_working:
                            stats['successful_requests'] += 1
                        
                        # Update success rate
                        proxy.success_rate = stats['successful_requests'] / stats['total_requests']
                        
                    except Exception as e:
                        self.logger.warning(f"Error testing proxy {proxy.host}: {e}")
                        proxy.is_working = False
                
                # Log health summary
                working_count = sum(1 for p in self.proxies if p.is_working)
                self.logger.info(f"Proxy health: {working_count}/{len(self.proxies)} working")
                
            except Exception as e:
                self.logger.error(f"Error in proxy health monitoring: {e}")
            
            # Wait for next check
            await asyncio.sleep(self.config.get('health_check_interval', 300))
    
    async def _test_proxy(self, proxy: ProxyConfig) -> bool:
        """Test if a proxy is working"""
        try:
            proxy_url = f"{proxy.protocol}://"
            if proxy.username and proxy.password:
                proxy_url += f"{proxy.username}:{proxy.password}@"
            proxy_url += f"{proxy.host}:{proxy.port}"
            
            connector = aiohttp.ProxyConnector.from_url(proxy_url)
            timeout = aiohttp.ClientTimeout(total=self.config.get('timeout', 30))
            
            async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
                # Test with a simple HTTP request
                start_time = time.time()
                async with session.get('http://httpbin.org/ip') as response:
                    if response.status == 200:
                        end_time = time.time()
                        proxy.speed_score = end_time - start_time
                        return True
            
            return False
            
        except Exception:
            return False
    
    async def handle_rate_limiting(self, domain: str):
        """Handle rate limiting for a specific domain"""
        if not self.config['rate_limiting']['enabled']:
            return
        
        now = datetime.now()
        
        # Clean old requests from history
        cutoff = now - timedelta(minutes=1)
        self.request_history = [req for req in self.request_history if req['timestamp'] > cutoff]
        
        # Count recent requests to this domain
        domain_requests = [req for req in self.request_history if req['domain'] == domain]
        
        requests_per_minute = self.config['rate_limiting']['requests_per_minute']
        burst_limit = self.config['rate_limiting']['burst_limit']
        
        # Check rate limits
        if len(domain_requests) >= requests_per_minute:
            self.logger.warning(f"Rate limit exceeded for {domain}, waiting...")
            await asyncio.sleep(60)  # Wait a minute
        
        elif len(domain_requests) >= burst_limit:
            # Add random delay for burst limit
            delay = random.uniform(5, 15)
            self.logger.info(f"Burst limit reached for {domain}, waiting {delay:.1f}s")
            await asyncio.sleep(delay)
        
        # Record this request
        self.request_history.append({
            'domain': domain,
            'timestamp': now
        })
    
    def record_detection(self, detection_type: str, url: str):
        """Record detection event"""
        self.detection_metrics.request_count += 1
        self.detection_metrics.last_detection = datetime.now().isoformat()
        
        if detection_type == 'blocked':
            self.detection_metrics.blocked_count += 1
            self.blocked_domains.add(url)
            
        elif detection_type == 'captcha':
            self.detection_metrics.captcha_count += 1
            
        # Update detection score
        total_requests = self.detection_metrics.request_count
        problematic_requests = (self.detection_metrics.blocked_count + 
                              self.detection_metrics.captcha_count)
        
        self.detection_metrics.detection_score = problematic_requests / total_requests if total_requests > 0 else 0
        
        # Log detection
        self.logger.warning(f"Detection recorded: {detection_type} at {url}")
        
        # If detection score is too high, rotate proxy
        if self.detection_metrics.detection_score > 0.3:  # 30% detection rate
            self.logger.warning("High detection rate, rotating proxy and backing off")
            self.current_proxy_index += 1  # Force proxy rotation
    
    def is_domain_blocked(self, domain: str) -> bool:
        """Check if a domain is blocked"""
        return domain in self.blocked_domains
    
    async def get_safe_delay(self) -> float:
        """Get a safe delay between requests based on detection metrics"""
        base_delay = 2.0  # Base 2 second delay
        
        # Increase delay based on detection score
        detection_multiplier = 1 + (self.detection_metrics.detection_score * 10)
        
        # Add randomization
        randomization = random.uniform(0.5, 1.5)
        
        final_delay = base_delay * detection_multiplier * randomization
        
        # Cap the delay
        return min(final_delay, 30.0)
    
    def get_proxy_stats(self) -> Dict:
        """Get proxy system statistics"""
        if not self.config.get('enabled'):
            return {'enabled': False}
        
        working_proxies = [p for p in self.proxies if p.is_working]
        
        return {
            'enabled': True,
            'total_proxies': len(self.proxies),
            'working_proxies': len(working_proxies),
            'current_proxy_index': self.current_proxy_index,
            'detection_metrics': asdict(self.detection_metrics),
            'blocked_domains': list(self.blocked_domains),
            'health_stats': self.proxy_health_stats
        }
    
    def save_proxy_stats(self):
        """Save proxy statistics to file"""
        output_dir = Path("data/proxy_stats")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        stats_file = output_dir / f"proxy_stats_{timestamp}.json"
        
        stats = self.get_proxy_stats()
        
        with open(stats_file, 'w') as f:
            json.dump(stats, f, indent=2)
        
        self.logger.info(f"💾 Proxy stats saved to: {stats_file}")

class AntiDetectionEnhancer:
    """Additional anti-detection measures"""
    
    @staticmethod
    async def simulate_human_behavior(page: Page):
        """Simulate human-like behavior on the page"""
        
        # Random mouse movements
        await page.mouse.move(random.randint(100, 800), random.randint(100, 600))
        await asyncio.sleep(random.uniform(0.1, 0.5))
        
        # Random scrolling
        if random.random() > 0.5:
            scroll_amount = random.randint(100, 500)
            await page.evaluate(f"window.scrollBy(0, {scroll_amount})")
            await asyncio.sleep(random.uniform(0.5, 1.5))
        
        # Occasional random clicks (on safe elements)
        if random.random() > 0.8:
            try:
                # Look for safe elements to click
                safe_selectors = ['body', 'div', 'span']
                selector = random.choice(safe_selectors)
                elements = await page.locator(selector).all()
                if elements:
                    element = random.choice(elements[:5])  # Click on first 5 elements only
                    await element.click(force=True)
                    await asyncio.sleep(random.uniform(0.2, 0.8))
            except:
                pass  # Ignore click errors
    
    @staticmethod
    async def randomize_timing(min_delay: float = 1.0, max_delay: float = 5.0):
        """Add random timing delays"""
        delay = random.uniform(min_delay, max_delay)
        await asyncio.sleep(delay)
    
    @staticmethod
    def detect_anti_bot_measures(page_content: str) -> List[str]:
        """Detect common anti-bot measures on the page"""
        detections = []
        
        content_lower = page_content.lower()
        
        # Common anti-bot indicators
        anti_bot_indicators = [
            ('cloudflare', 'Checking your browser'),
            ('captcha', 'captcha'),
            ('blocked', 'access denied'),
            ('rate_limit', 'too many requests'),
            ('bot_detection', 'suspicious activity'),
            ('verification', 'please verify you are human')
        ]
        
        for indicator_type, keyword in anti_bot_indicators:
            if keyword in content_lower:
                detections.append(indicator_type)
        
        return detections

async def main():
    """Demo function"""
    print("🔄 PROXY ROTATION & ANTI-DETECTION SYSTEM")
    print("🛡️ Advanced measures for undetected scraping")
    print("="*60)
    
    # Initialize proxy system
    proxy_system = ProxyRotationSystem()
    
    # Show stats
    stats = proxy_system.get_proxy_stats()
    
    print(f"📊 Proxy System Status:")
    print(f"   🔄 Enabled: {stats['enabled']}")
    if stats['enabled']:
        print(f"   🌐 Total proxies: {stats['total_proxies']}")
        print(f"   ✅ Working proxies: {stats['working_proxies']}")
        print(f"   🎯 Detection score: {stats['detection_metrics']['detection_score']:.2%}")
    
    print(f"\n💡 Features available:")
    print(f"   • Automatic proxy rotation")
    print(f"   • Health monitoring and failover")
    print(f"   • User agent rotation")
    print(f"   • Browser fingerprint randomization")
    print(f"   • Rate limiting and backoff")
    print(f"   • Anti-detection measures")
    print(f"   • Human behavior simulation")
    
    print(f"\n✅ Proxy rotation system ready!")

if __name__ == "__main__":
    asyncio.run(main())