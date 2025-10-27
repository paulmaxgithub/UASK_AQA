"""
Pytest configuration and fixtures
"""
import pytest
import logging
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page
from pathlib import Path
from typing import Generator

from config import (
    BrowserConfig,
    TestConfig,
    ENGLISH_URL,
    ARABIC_URL,
    SCREENSHOTS_DIR
)
from utils.logger import setup_logger
from utils.test_helpers import ScreenshotHelper
from pages.chat_page import ChatPage

# Setup logging
logger = setup_logger(__name__)


def pytest_addoption(parser):
    """Add custom command line options"""
    parser.addoption(
        "--browser",
        action="store",
        default=BrowserConfig.BROWSER_TYPE,
        help="Browser to use: chromium, firefox, or webkit"
    )
    parser.addoption(
        "--headless",
        action="store_true",
        default=BrowserConfig.HEADLESS,
        help="Run browser in headless mode"
    )
    parser.addoption(
        "--language",
        action="store",
        default=TestConfig.DEFAULT_LANGUAGE,
        help="Test language: en or ar"
    )
    parser.addoption(
        "--slow-mo",
        action="store",
        type=int,
        default=BrowserConfig.SLOW_MO,
        help="Slow down operations by N milliseconds"
    )
    parser.addoption(
        "--stealth",
        action="store_true",
        default=False,
        help="Enable stealth mode to bypass CAPTCHA (requires browser_config.py)"
    )
    parser.addoption(
        "--session-file",
        action="store",
        default=None,
        help="Path to saved session file for CAPTCHA bypass"
    )


@pytest.fixture(scope="session")
def browser_type(request):
    """Get browser type from command line"""
    return request.config.getoption("--browser")


@pytest.fixture(scope="session")
def headless(request):
    """Get headless mode from command line"""
    return request.config.getoption("--headless")


@pytest.fixture(scope="session")
def test_language(request):
    """Get test language from command line"""
    return request.config.getoption("--language")


@pytest.fixture(scope="session")
def slow_mo(request):
    """Get slow-mo value from command line"""
    return request.config.getoption("--slow-mo")


@pytest.fixture(scope="session")
def playwright():
    """Playwright instance - session scoped"""
    with sync_playwright() as p:
        logger.info("Starting Playwright")
        yield p
        logger.info("Stopping Playwright")


@pytest.fixture(scope="session")
def browser(playwright, browser_type, headless, slow_mo) -> Generator[Browser, None, None]:
    """
    Browser instance - session scoped
    Reused across all tests for better performance
    """
    logger.info(f"Launching {browser_type} browser (headless={headless})")

    browser_types = {
        "chromium": playwright.chromium,
        "firefox": playwright.firefox,
        "webkit": playwright.webkit
    }

    browser_launcher = browser_types.get(browser_type, playwright.chromium)

    browser = browser_launcher.launch(
        headless=headless,
        slow_mo=slow_mo
    )

    yield browser

    logger.info("Closing browser")
    browser.close()


@pytest.fixture(scope="function")
def stealth_mode(request):
    """Check if stealth mode is enabled"""
    return request.config.getoption("--stealth")


@pytest.fixture(scope="function")
def session_file_path(request):
    """Get session file path if provided"""
    return request.config.getoption("--session-file")


@pytest.fixture(scope="function")
def context(browser: Browser, stealth_mode: bool, session_file_path: str) -> Generator[BrowserContext, None, None]:
    """
    Browser context - function scoped
    Creates isolated context for each test
    """
    from utils.browser_config import StealthBrowserConfig, RecaptchaHelper
    
    if stealth_mode:
        logger.info("Creating STEALTH browser context")
        context = StealthBrowserConfig.create_stealth_context(browser)
        
        if session_file_path:
            logger.info(f"Loading saved session from: {session_file_path}")
            RecaptchaHelper.use_saved_session(context, session_file_path)
    else:
        logger.info("Creating browser context")
        
        # Загружаем сессию если указана (БЕЗ stealth)
        storage_state = None
        if session_file_path:
            import json
            from pathlib import Path
            
            if Path(session_file_path).exists():
                logger.info(f"Loading saved session from: {session_file_path}")
                with open(session_file_path, 'r') as f:
                    session_data = json.load(f)
                
                storage_state = {
                    "cookies": session_data.get('cookies', []),
                    "origins": session_data.get('storage', {}).get('local_storage', [])
                }
                logger.info(f"✓ Loaded {len(storage_state['cookies'])} cookies")
            else:
                logger.warning(f"Session file not found: {session_file_path}")
        
        context = browser.new_context(
            viewport={
                "width": BrowserConfig.VIEWPORT_WIDTH,
                "height": BrowserConfig.VIEWPORT_HEIGHT
            },
            locale="en-US",
            timezone_id="Asia/Dubai",
            storage_state=storage_state,  # Загружаем сессию при создании контекста
        )

    context.set_default_timeout(BrowserConfig.TIMEOUT)
    yield context
    logger.info("Closing browser context")
    context.close()


@pytest.fixture(scope="function")
def page(context: BrowserContext) -> Generator[Page, None, None]:
    """
    Page instance - function scoped
    New page for each test
    """
    logger.info("Creating new page")
    page = context.new_page()

    yield page

    logger.info("Closing page")
    page.close()


@pytest.fixture(scope="function")
def mobile_page(browser: Browser) -> Generator[Page, None, None]:
    """
    Mobile page instance - function scoped
    For mobile-specific tests
    """
    logger.info(f"Creating mobile page ({BrowserConfig.MOBILE_DEVICE})")

    mobile_context = browser.new_context(
        **browser.devices[BrowserConfig.MOBILE_DEVICE]
    )

    mobile_context.set_default_timeout(BrowserConfig.TIMEOUT)
    page = mobile_context.new_page()

    yield page

    logger.info("Closing mobile page")
    page.close()
    mobile_context.close()


@pytest.fixture(scope="function")
def stealth_page(request, browser: Browser) -> Generator[Page, None, None]:
    """
    Create a stealth page for bypassing CAPTCHA
    
    Usage:
        pytest --stealth
        pytest --stealth --session-file saved_session.json
    """
    from utils.browser_config import create_optimal_test_browser
    
    session_file = request.config.getoption("--session-file")
    context, page = create_optimal_test_browser(browser, session_file)
    
    yield page
    
    page.close()
    context.close()


@pytest.fixture(scope="function")
def chatbot_page(page: Page, test_language: str) -> ChatPage:
    """
    ChatPage instance with navigation

    Args:
        page: Playwright Page
        test_language: Language to test (en or ar)

    Returns:
        ChatPage instance
    """
    logger.info(f"Initializing ChatPage for language: {test_language}")

    chatbot = ChatPage(page)

    # Navigate to appropriate URL based on language
    url = ENGLISH_URL if test_language == "en" else ARABIC_URL
    chatbot.navigate(url)

    # Wait for chat widget to load
    try:
        chatbot.wait_for_chat_widget(timeout=15000)
    except Exception as e:
        logger.error(f"Failed to load chat widget: {e}")
        # Take screenshot for debugging
        if TestConfig.SCREENSHOT_ON_FAILURE:
            chatbot.take_screenshot("chat_widget_load_failure")
        raise

    return chatbot


@pytest.fixture(scope="function")
def mobile_chatbot_page(mobile_page: Page, test_language: str) -> ChatPage:
    """Mobile chatbot page instance"""
    logger.info(f"Initializing mobile ChatPage for language: {test_language}")

    chatbot = ChatPage(mobile_page)
    url = ENGLISH_URL if test_language == "en" else ARABIC_URL
    chatbot.navigate(url)

    try:
        chatbot.wait_for_chat_widget(timeout=15000)
    except Exception as e:
        logger.error(f"Failed to load mobile chat widget: {e}")
        if TestConfig.SCREENSHOT_ON_FAILURE:
            chatbot.take_screenshot("mobile_chat_widget_load_failure")
        raise

    return chatbot


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Hook to capture test results and take screenshots on failure
    """
    outcome = yield
    report = outcome.get_result()

    # Only process on test call phase (not setup/teardown)
    if report.when == "call":
        # Get the page fixture if available
        if "page" in item.funcargs or "chatbot_page" in item.funcargs:
            if report.failed and TestConfig.SCREENSHOT_ON_FAILURE:
                # Get page from either fixture
                chatbot = item.funcargs.get("chatbot_page")
                page_obj = item.funcargs.get("page")

                screenshot_name = ScreenshotHelper.generate_screenshot_name(
                    item.name,
                    "failed"
                )

                try:
                    if chatbot:
                        screenshot_path = chatbot.take_screenshot(screenshot_name)
                        logger.info(f"Screenshot saved: {screenshot_path}")

                        # Save metadata
                        ScreenshotHelper.save_screenshot_metadata(
                            screenshot_path,
                            item.name,
                            {
                                "error": str(report.longrepr),
                                "test_phase": report.when
                            }
                        )
                    elif page_obj:
                        screenshot_path = SCREENSHOTS_DIR / screenshot_name
                        page_obj.screenshot(path=str(screenshot_path))
                        logger.info(f"Screenshot saved: {screenshot_path}")
                except Exception as e:
                    logger.error(f"Failed to capture screenshot: {e}")


@pytest.fixture(scope="session", autouse=True)
def test_session_setup():
    """
    Session-level setup and teardown
    Runs once before all tests and once after
    """
    logger.info("=" * 80)
    logger.info("Starting Test Session")
    logger.info("=" * 80)

    yield

    logger.info("=" * 80)
    logger.info("Test Session Complete")
    logger.info("=" * 80)


@pytest.fixture(scope="function", autouse=True)
def test_case_logger(request):
    """
    Log test case start and end
    """
    logger.info(f"Starting test: {request.node.name}")

    yield

    logger.info(f"Finished test: {request.node.name}")
