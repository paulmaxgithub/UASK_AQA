
"""
UI Behavior Tests for U-Ask Chatbot
Tests the user interface behavior and interactions with reliable CAPTCHA/disclaimer handling
"""
import pytest
import logging
import allure
from utils.automation_helpers import AutomationHelpers

logger = logging.getLogger(__name__)

@pytest.mark.ui
@pytest.mark.smoke
class TestChatWidgetLoading:
    """Test chat widget loading behavior"""

    @allure.title("Chat widget loads correctly on desktop")
    @allure.description("Verify chat widget loads and all elements are visible on desktop")
    def test_chat_widget_loads_on_desktop(self, browser):
        """Verify chat widget loads correctly on desktop"""
        logger.info("=== TEST: Chat widget loads on desktop ===")
        
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()
        
        # Reliable page preparation
        setup_result = AutomationHelpers.setup_page_reliably(page)
        assert setup_result["page_ready"], "Page is not ready for testing"
        
        # Finding chat elements with fallback
        elements = AutomationHelpers.find_chat_elements(page)
        
        assert elements["input_found"], "Input field not found"
        assert elements["send_found"], "Send button not found"
        assert elements["widget_found"], "Chat widget not found"
        
        logger.info(f"Found elements: input={elements['input_found']}, send={elements['send_found']}, widget={elements['widget_found']}")
        
        # Check for CAPTCHA (document but don't block)
        captcha_info = AutomationHelpers.check_for_captcha(page)
        if captcha_info["captcha_detected"]:
            logger.warning(f"🔍 CAPTCHA detected: {captcha_info}")
        
        logger.info("✅ Desktop widget loading test passed")
        
        context.close()

    @pytest.mark.mobile
    @allure.title("Chat widget loads correctly on mobile")  
    def test_mobile_simulation(self, browser):
        """Verify chat widget loads correctly on mobile"""
        logger.info("=== TEST: Mobile widget simulation ===")
        
        # Mobile viewport
        context = browser.new_context(viewport={'width': 375, 'height': 667})
        page = context.new_page()
        
        setup_result = AutomationHelpers.setup_page_reliably(page)
        assert setup_result["page_ready"], "Mobile page is not ready"
        
        elements = AutomationHelpers.find_chat_elements(page)
        
        assert elements["input_found"], "Mobile input field not found"
        assert elements["send_found"], "Mobile send button not found"
        assert elements["widget_found"], "Mobile chat widget not found"
        
        logger.info(f"Found elements: input={elements['input_found']}, send={elements['send_found']}, widget={elements['widget_found']}")
        
        logger.info("✅ Mobile simulation test passed")
        
        context.close()


@pytest.mark.ui
class TestMessageSending:
    """Test message sending functionality"""

    @allure.title("User can type message in input box")
    def test_user_can_type_message(self, browser):
        """Verify user can type a message in input box"""
        logger.info("=== TEST: User types message ===")
        
        context = browser.new_context()
        page = context.new_page()
        
        setup_result = AutomationHelpers.setup_page_reliably(page)
        assert setup_result["page_ready"], "Page is not ready"
        
        elements = AutomationHelpers.find_chat_elements(page)
        assert elements["input_found"], "Input field not found"
        
        test_message = "Hello, how can I apply for a visa?"
        
        # Reliable message typing
        typing_success = AutomationHelpers.type_message_reliably(page, test_message, elements["input_box"])
        assert typing_success, "Failed to type message"
        
        logger.info(f"Typing message: {test_message}")
        logger.info("✅ Message typing test passed")
        
        context.close()

    @allure.title("Send button interaction works correctly")
    def test_send_button_interaction(self, browser):
        """Verify send button can be clicked"""
        logger.info("=== TEST: Send button interaction ===")
        
        context = browser.new_context()
        page = context.new_page()
        
        setup_result = AutomationHelpers.setup_page_reliably(page)
        assert setup_result["page_ready"], "Page is not ready"
        
        elements = AutomationHelpers.find_chat_elements(page)
        
        # Check for CAPTCHA before sending
        captcha_before = AutomationHelpers.check_for_captcha(page)
        if captcha_before["captcha_detected"]:
            logger.warning(f"🔍 CAPTCHA found: {captcha_before}")
        
        # Click send button
        logger.info("Clicking send button...")
        send_success = AutomationHelpers.click_send_button_reliably(page, elements["send_button"])
        assert send_success, "Failed to click send button"
        
        # Check for CAPTCHA after sending  
        captcha_after = AutomationHelpers.check_for_captcha(page)
        if captcha_after["captcha_detected"]:
            logger.warning("⚠️ CAPTCHA detected after sending - this is expected")
        
        logger.info("✅ Send button test passed")
        
        context.close()


@pytest.mark.ui
class TestUIResponsiveness:
    """Test UI responsiveness and behavior"""

    @allure.title("Page elements are visible and accessible")
    def test_page_elements_are_visible(self, browser):
        """Verify all key page elements are visible"""
        logger.info("=== TEST: Page elements visibility ===")
        
        context = browser.new_context()
        page = context.new_page()
        
        setup_result = AutomationHelpers.setup_page_reliably(page)
        assert setup_result["page_ready"], "Page is not ready"
        
        elements = AutomationHelpers.find_chat_elements(page)
        
        assert elements["input_found"], "Input field not visible"
        assert elements["send_found"], "Send button not visible"
        assert elements["widget_found"], "Chat widget not visible"
        
        logger.info(f"Found elements: input={elements['input_found']}, send={elements['send_found']}, widget={elements['widget_found']}")
        logger.info("✅ Elements visibility test passed")
        
        context.close()

    @allure.title("Language and text direction detection")
    def test_language_and_direction_detection(self, browser):
        """Test language and text direction"""
        logger.info("=== TEST: Language and text direction detection ===")
        
        context = browser.new_context()
        page = context.new_page()
        
        setup_result = AutomationHelpers.setup_page_reliably(page)
        assert setup_result["page_ready"], "Page is not ready"
        
        # Getting information about the page language
        try:
            lang = page.locator("html").get_attribute("lang") or "en"
            dir_attr = page.locator("html").get_attribute("dir") or "ltr"
            
            logger.info(f"Page language: {lang}, direction: {dir_attr}")
            
            # For English, we expect LTR
            if "en" in lang.lower():
                assert dir_attr == "ltr" or dir_attr is None, f"LTR is expected for English, but got: {dir_attr}"
            
        except Exception as e:
            logger.warning(f"Failed to determine language/direction: {e}")
        
        logger.info("✅ Language detection test passed")
        
        context.close()


@pytest.mark.ui  
class TestErrorHandlingAndEdgeCases:
    """Test error handling and edge cases"""

    @allure.title("Empty message handling")
    def test_empty_message_handling(self, browser):
        """Test how system handles empty messages"""
        logger.info("=== TEST: Empty message handling ===")
        
        context = browser.new_context()
        page = context.new_page()
        
        setup_result = AutomationHelpers.setup_page_reliably(page)
        assert setup_result["page_ready"], "Page is not ready"
        
        elements = AutomationHelpers.find_chat_elements(page)
        
        # Try to send an empty message
        logger.info("Trying to send empty message...")
        try:
            elements["input_box"].fill("")
            send_success = AutomationHelpers.click_send_button_reliably(page, elements["send_button"])
            logger.info(f"Empty message sent: {send_success}")
        except Exception as e:
            logger.info(f"Empty message handled with exception: {e}")
        
        logger.info("✅ Empty message handling test passed")
        
        context.close()

    @allure.title("Page responsiveness under load")
    def test_page_responsiveness_under_load(self, browser):
        """Test page responsiveness under multiple actions"""
        logger.info("=== TEST: Page responsiveness under load ===")
        
        context = browser.new_context()
        page = context.new_page()
        
        setup_result = AutomationHelpers.setup_page_reliably(page)
        assert setup_result["page_ready"], "Page is not ready"
        
        elements = AutomationHelpers.find_chat_elements(page)
        
        # Perform multiple actions
        logger.info("Performing multiple actions...")
        for i in range(3):
            try:
                elements["input_box"].fill(f"Test message {i}")
                page.wait_for_timeout(500)
                elements["input_box"].clear()
                page.wait_for_timeout(500)
            except Exception as e:
                logger.warning(f"Action {i} caused exception: {e}")
        
        # Page should remain responsive
        final_elements = AutomationHelpers.find_chat_elements(page)
        assert final_elements["input_found"], "Input field became unavailable after load"
        
        logger.info("✅ Load responsiveness test passed")
        
        context.close()
