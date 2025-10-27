"""
Stealth Browser Configuration
Legal approaches to minimize reCAPTCHA triggers for automated testing
"""
import json
from typing import Optional, Dict, Any
from playwright.sync_api import Browser, BrowserContext, Page
import logging

logger = logging.getLogger(__name__)


class StealthBrowserConfig:
    """
    Creates a browser context that mimics real user behavior
    to reduce reCAPTCHA triggers legally
    """

    @staticmethod
    def get_realistic_user_agent() -> str:
        """Return realistic user agent string"""
        return (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )

    @staticmethod
    def get_realistic_viewport() -> Dict[str, int]:
        """Return realistic viewport size"""
        return {"width": 1920, "height": 1080}

    @staticmethod
    def get_context_options() -> Dict[str, Any]:
        """
        Return browser context options that make automation look more human

        Legal approach: Configure browser to behave like a real user
        - Realistic user agent
        - Common screen resolution
        - Proper locale and timezone
        - Accept language headers
        """
        return {
            "user_agent": StealthBrowserConfig.get_realistic_user_agent(),
            "viewport": StealthBrowserConfig.get_realistic_viewport(),
            "locale": "en-US",
            "timezone_id": "America/New_York",
            "geolocation": {"longitude": -74.006, "latitude": 40.7128},  # New York
            "permissions": ["geolocation"],
            "color_scheme": "light",
            "has_touch": False,
            "is_mobile": False,
            "device_scale_factor": 1,
            "extra_http_headers": {
                "Accept-Language": "en-US,en;q=0.9",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
            }
        }

    @staticmethod
    def get_stealth_scripts() -> list[str]:
        """
        Return JavaScript to inject that makes automation less detectable

        Legal approach: Override automation-specific properties
        These are standard stealth techniques used in legitimate testing
        """
        return [
            # Override navigator.webdriver (only once)
            """
            try {
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            } catch(e) {
                // Already defined
            }
            """,

            # Add realistic plugins
            """
            try {
                Object.defineProperty(navigator, 'plugins', {
                get: () => [
                    {
                        0: {type: "application/pdf", suffixes: "pdf", description: "Portable Document Format"},
                        description: "Portable Document Format",
                        filename: "internal-pdf-viewer",
                        length: 1,
                        name: "Chrome PDF Plugin"
                    },
                    {
                        0: {type: "application/x-google-chrome-pdf", suffixes: "pdf", description: "Portable Document Format"},
                        description: "Portable Document Format",
                        filename: "internal-pdf-viewer",
                        length: 1,
                        name: "Chrome PDF Viewer"
                    },
                    {
                        description: "Native Client Executable",
                        filename: "internal-nacl-plugin",
                        length: 2,
                        name: "Native Client"
                    }
                ]
            });
            } catch(e) { /* Already defined */ }
            """,

            # Add chrome property
            """
            window.chrome = {
                runtime: {},
                loadTimes: function() {},
                csi: function() {},
                app: {}
            };
            """,

            # Mock languages
            """
            try {
                Object.defineProperty(navigator, 'languages', {
                get: () => ['en187', 'en']
            });
            } catch(e) { /* Already defined */ }
            """,
            
            # Hide automation indicators
            """
            Object.defineProperty(navigator, 'hardwareConcurrency', {
                get: () => 8
            });
            } catch(e) { /* Already defined */ }
            """,
            
            # Mock device memory
            """
            Object.defineProperty(navigator, 'deviceMemory', {
                get: () => 8
            });
            } catch(e) { /* Already defined */ }
            """,
            
            # Override permission prompts
            """
            try {
                const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    parameters.name === 'geolocation' ?
                    Promise.resolve({ state: 'granted' }) :
                    originalQuery(parameters)
            );
            """,
        ]

    @staticmethod
    def create_stealth_context(browser: Browser) -> BrowserContext:
        """
        Create a browser context with stealth configuration

        Args:
            browser: Playwright browser instance

        Returns:
            Configured browser context
        """
        logger.info("Creating stealth browser context...")

        context = browser.new_context(**StealthBrowserConfig.get_context_options())

        # Add init scripts to every page in this context
        for script in StealthBrowserConfig.get_stealth_scripts():
            context.add_init_script(script)

        logger.info("✓ Stealth context created")
        return context

    @staticmethod
    def create_stealth_page(context: BrowserContext) -> Page:
        """
        Create a page with additional human-like behaviors

        Args:
            context: Browser context

        Returns:
            Page object
        """
        page = context.new_page()

        # Set additional page properties
        page.set_extra_http_headers({
            "DNT": "1",  # Do Not Track
            "Sec-CH-UA": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            "Sec-CH-UA-Mobile": "?0",
            "Sec-CH-UA-Platform": '"macOS"',
        })

        logger.info("✓ Stealth page created")
        return page


class HumanBehaviorSimulator:
    """
    Simulate human-like interactions to reduce bot detection
    Legal approach: Make automation behave like a real user
    """

    @staticmethod
    def human_type(page: Page, selector: str, text: str, delay_ms: int = 100):
        """
        Type text with human-like delays between characters

        Args:
            page: Playwright page
            selector: Element selector
            text: Text to type
            delay_ms: Delay between keystrokes in milliseconds
        """
        logger.info(f"Typing with human-like delays: {text[:50]}...")
        element = page.locator(selector).first

        # Click with slight delay
        element.click()
        page.wait_for_timeout(300)

        # Type character by character with random-ish delays
        for i, char in enumerate(text):
            element.type(char, delay=delay_ms + (i % 30))  # Slight variation

        logger.info("✓ Human-like typing completed")

    @staticmethod
    def human_mouse_move(page: Page, x: int, y: int):
        """
        Move mouse in a human-like curved path

        Args:
            page: Playwright page
            x: Target X coordinate
            y: Target Y coordinate
        """
        # Get current mouse position (approximate)
        # Move in small steps to simulate human movement
        page.mouse.move(x, y, steps=10)
        logger.debug(f"Mouse moved to ({x}, {y})")

    @staticmethod
    def random_scroll(page: Page):
        """
        Scroll page randomly to simulate reading behavior

        Args:
            page: Playwright page
        """
        logger.info("Simulating human scroll behavior...")

        # Scroll down a bit
        page.evaluate("window.scrollBy(0, 300)")
        page.wait_for_timeout(500)

        # Scroll up a bit (like user is reading)
        page.evaluate("window.scrollBy(0, -100)")
        page.wait_for_timeout(300)

        # Scroll back to top
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(200)

        logger.info("✓ Scroll simulation completed")

    @staticmethod
    def pause_like_reading(page: Page, duration_ms: int = 2000):
        """
        Pause as if user is reading content

        Args:
            page: Playwright page
            duration_ms: Duration in milliseconds
        """
        logger.debug(f"Pausing {duration_ms}ms (simulating reading)...")
        page.wait_for_timeout(duration_ms)


class RecaptchaHelper:
    """
    Helper methods for dealing with reCAPTCHA legally
    """

    @staticmethod
    def wait_for_human_solve(page: Page, timeout_ms: int = 120000) -> bool:
        """
        Legal approach: Pause automation and let human solve reCAPTCHA
        Useful for manual test runs or development

        Args:
            page: Playwright page
            timeout_ms: Max time to wait

        Returns:
            True if solved, False if timeout
        """
        logger.warning("⏸️  reCAPTCHA DETECTED - Please solve manually")
        logger.warning("⏸️  Waiting up to 120 seconds for human intervention...")

        try:
            # Wait for reCAPTCHA iframe to disappear
            page.locator("iframe[src*='recaptcha']").first.wait_for(
                state="hidden",
                timeout=timeout_ms
            )
            logger.info("✓ reCAPTCHA solved! Continuing automation...")
            return True
        except Exception as e:
            logger.error(f"✗ Timeout waiting for reCAPTCHA solve: {e}")
            return False

    @staticmethod
    def is_recaptcha_present(page: Page) -> bool:
        """
        Check if reCAPTCHA is currently visible

        Args:
            page: Playwright page

        Returns:
            True if reCAPTCHA is visible
        """
        try:
            recaptcha = page.locator("iframe[src*='recaptcha']").first
            return recaptcha.is_visible(timeout=2000)
        except:
            return False

    @staticmethod
    def use_saved_session(context: BrowserContext, session_file: str):
        """
        Legal approach: Reuse authenticated session from real user

        This is the BEST approach for testing:
        1. Manually login once and save session
        2. Reuse session for all automated tests
        3. reCAPTCHA trusts the session

        Args:
            context: Browser context
            session_file: Path to saved session JSON
        """
        logger.info(f"Loading session from {session_file}...")

        try:
            with open(session_file, 'r') as f:
                session_data = json.load(f)

            # Prepare storage state for context
            storage_state = {
                "cookies": session_data.get('cookies', []),
                "origins": session_data.get('storage', {}).get('local_storage', [])
            }
            
            logger.info(f"✓ Prepared storage state: {len(storage_state['cookies'])} cookies, {len(storage_state['origins'])} origins")

            # Save current context
            context.close()
            
            # Create new context with storage state
            new_context = context.browser.new_context(
                storage_state=storage_state
            )
            
            # Copy to original context reference
            context = new_context
            
            logger.info(f"✓ Loaded {len(storage_state['cookies'])} domains with localStorage")
            logger.info("✓ Session loaded successfully")
            return True

        except Exception as e:
            logger.error(f"✗ Could not load session: {e}")
            return False

    @staticmethod
    def save_session(page: Page, session_file: str):
        """
        Save current session for reuse

        Run this once manually after solving reCAPTCHA:
        1. Start browser
        2. Manually interact and solve reCAPTCHA
        3. Call this method to save session
        4. Reuse session in all future tests

        Args:
            page: Playwright page
            session_file: Path to save session JSON
        """
        logger.info(f"Saving session to {session_file}...")

        session_data = {
            'cookies': page.context.cookies(),
            'localStorage': page.evaluate('() => Object.entries(localStorage)'),
            'url': page.url
        }

        with open(session_file, 'w') as f:
            json.dump(session_data, f, indent=2)

        logger.info(f"✓ Session saved ({len(session_data['cookies'])} cookies)")
        logger.info(f"✓ Reuse this session to bypass reCAPTCHA in future tests")


def create_optimal_test_browser(browser: Browser, session_file: Optional[str] = None) -> tuple[BrowserContext, Page]:
    """
    Create optimally configured browser for testing with minimal reCAPTCHA triggers

    Combines multiple legal techniques:
    1. Stealth configuration
    2. Session reuse (if available)
    3. Human-like behavior simulation

    Args:
        browser: Playwright browser
        session_file: Optional path to saved session

    Returns:
        Tuple of (context, page)
    """
    logger.info("🔧 Creating optimal test browser...")

    # Create stealth context
    context = StealthBrowserConfig.create_stealth_context(browser)

    # Load saved session if available
    if session_file:
        RecaptchaHelper.use_saved_session(context, session_file)

    # Create stealth page
    page = StealthBrowserConfig.create_stealth_page(context)

    logger.info("✅ Optimal test browser ready!")
    logger.info("📌 Tips:")
    logger.info("   - Use HumanBehaviorSimulator for interactions")
    logger.info("   - Add pauses between actions (1-3 seconds)")
    logger.info("   - Scroll and move mouse naturally")
    logger.info("   - Save session after first successful run")

    return context, page
