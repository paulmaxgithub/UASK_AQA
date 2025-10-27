"""
Page Object Model for U-Ask Chatbot
Implements interactions with the chatbot interface
"""
from typing import Optional, List
from playwright.sync_api import Page, Locator
from config import Selectors, TestConfig
import logging

logger = logging.getLogger(__name__)


class ChatPage:
    """
    Page Object for U-Ask chatbot interface
    Encapsulates all interactions with the chatbot UI
    """

    def __init__(self, page: Page):
        """
        Initialize ChatPage with Playwright page object

        Args:
            page: Playwright Page instance
        """
        self.page = page
        self.timeout = TestConfig.MAX_RESPONSE_TIME

    # Locators
    @property
    def chat_widget(self) -> Locator:
        """Chat widget container"""
        # Multiple possible selectors for flexibility
        return self.page.locator(
            f"{Selectors.CHAT_WIDGET}, iframe[title*='chat'], #chat-container"
        ).first

    @property
    def input_box(self) -> Locator:
        """Chat input field"""
        return self.page.locator(
            f"{Selectors.INPUT_BOX}, textarea, input[placeholder]"
        ).first

    @property
    def send_button(self) -> Locator:
        """Send message button"""
        return self.page.locator(
            f"{Selectors.SEND_BUTTON}, button:has-text('Send'), button[aria-label*='send' i]"
        ).first

    @property
    def message_container(self) -> Locator:
        """Container with all messages"""
        return self.page.locator(
            f"{Selectors.MESSAGE_CONTAINER}, .messages, [role='log']"
        ).first

    @property
    def user_messages(self) -> Locator:
        """All user messages"""
        return self.page.locator(
            f"{Selectors.USER_MESSAGE}, .user, [data-message-type='user']"
        )

    @property
    def ai_responses(self) -> Locator:
        """All AI responses"""
        return self.page.locator(
            f"{Selectors.AI_RESPONSE}, .assistant, .bot, [data-message-type='assistant']"
        )

    @property
    def loading_indicator(self) -> Locator:
        """Loading/typing indicator"""
        return self.page.locator(
            f"{Selectors.LOADING_INDICATOR}, .spinner, [role='progressbar']"
        )

    @property
    def error_message(self) -> Locator:
        """Error message display"""
        return self.page.locator(
            f"{Selectors.ERROR_MESSAGE}, .error, [role='alert']"
        )

    # Actions
    def navigate(self, url: str) -> None:
        """
        Navigate to the specified URL

        Args:
            url: URL to navigate to
        """
        logger.info(f"Navigating to {url}")
        self.page.goto(url, wait_until="domcontentloaded", timeout=self.timeout)
        self.page.wait_for_load_state("networkidle", timeout=self.timeout)

    def wait_for_chat_widget(self, timeout: Optional[int] = None) -> None:
        """
        Wait for chat widget to be visible

        Args:
            timeout: Custom timeout in ms (uses default if None)
        """
        timeout = timeout or self.timeout
        logger.info("Waiting for chat widget to load")

        # Try multiple strategies to find chat widget
        try:
            self.chat_widget.wait_for(state="visible", timeout=timeout)
        except Exception as e:
            # If widget is in iframe, try to find and switch
            iframe = self.page.frame_locator("iframe").first
            if iframe:
                logger.info("Chat widget found in iframe")
                return
            raise e

    def send_message(self, message: str, wait_for_response: bool = True) -> None:
        """
        Send a message in the chat

        Args:
            message: Message text to send
            wait_for_response: Whether to wait for AI response
        """
        logger.info(f"Sending message: {message[:50]}...")

        # Ensure input is visible and ready
        self.input_box.wait_for(state="visible", timeout=self.timeout)

        # Clear any existing text
        self.input_box.clear()

        # Type message
        self.input_box.fill(message)

        # Small delay to ensure text is filled
        self.page.wait_for_timeout(500)

        # Click send button
        self.send_button.click()

        if wait_for_response:
            self.wait_for_response()

    def wait_for_response(self, timeout: Optional[int] = None) -> None:
        """
        Wait for AI response to appear

        Args:
            timeout: Custom timeout in ms
        """
        timeout = timeout or TestConfig.MAX_RESPONSE_TIME_AI
        logger.info("Waiting for AI response")

        # Wait for loading indicator to appear and disappear
        try:
            self.loading_indicator.wait_for(state="visible", timeout=5000)
            self.loading_indicator.wait_for(state="hidden", timeout=timeout)
        except Exception:
            # Loading indicator might not appear for fast responses
            pass

        # Ensure at least one AI response is visible
        self.ai_responses.first.wait_for(state="visible", timeout=timeout)

        # Small delay to ensure response is fully rendered
        self.page.wait_for_timeout(1000)

    def get_last_ai_response(self) -> str:
        """
        Get the text of the last AI response

        Returns:
            Text content of the last AI response
        """
        logger.info("Getting last AI response")
        responses = self.ai_responses.all()

        if not responses:
            logger.warning("No AI responses found")
            return ""

        last_response = responses[-1]
        text = last_response.inner_text()
        logger.info(f"Last response: {text[:100]}...")
        return text

    def get_all_ai_responses(self) -> List[str]:
        """
        Get all AI responses in the conversation

        Returns:
            List of AI response texts
        """
        logger.info("Getting all AI responses")
        return [response.inner_text() for response in self.ai_responses.all()]

    def get_last_user_message(self) -> str:
        """
        Get the text of the last user message

        Returns:
            Text content of the last user message
        """
        messages = self.user_messages.all()
        return messages[-1].inner_text() if messages else ""

    def is_input_cleared(self) -> bool:
        """
        Check if input field is empty after sending

        Returns:
            True if input is empty, False otherwise
        """
        input_value = self.input_box.input_value()
        return len(input_value.strip()) == 0

    def get_text_direction(self) -> str:
        """
        Get text direction (ltr or rtl) of the page

        Returns:
            'ltr' or 'rtl'
        """
        direction = self.page.evaluate("document.dir || document.documentElement.dir")
        return direction or "ltr"

    def is_rtl_layout(self) -> bool:
        """
        Check if the page is using RTL layout (for Arabic)

        Returns:
            True if RTL, False if LTR
        """
        return self.get_text_direction() == "rtl"

    def scroll_to_bottom(self) -> None:
        """Scroll chat container to bottom"""
        logger.info("Scrolling to bottom")
        self.message_container.evaluate("el => el.scrollTop = el.scrollHeight")

    def get_message_count(self) -> dict:
        """
        Get count of user and AI messages

        Returns:
            Dict with 'user' and 'ai' message counts
        """
        return {
            "user": self.user_messages.count(),
            "ai": self.ai_responses.count()
        }

    def is_error_displayed(self) -> bool:
        """
        Check if an error message is displayed

        Returns:
            True if error is visible, False otherwise
        """
        try:
            return self.error_message.is_visible()
        except Exception:
            return False

    def get_error_message(self) -> str:
        """
        Get error message text if displayed

        Returns:
            Error message text or empty string
        """
        if self.is_error_displayed():
            return self.error_message.inner_text()
        return ""

    def is_loading(self) -> bool:
        """
        Check if loading indicator is visible

        Returns:
            True if loading, False otherwise
        """
        try:
            return self.loading_indicator.is_visible()
        except Exception:
            return False

    def take_screenshot(self, name: str) -> str:
        """
        Take screenshot of the page

        Args:
            name: Screenshot filename (without extension)

        Returns:
            Path to saved screenshot
        """
        from config import SCREENSHOTS_DIR
        import datetime

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}.png"
        filepath = SCREENSHOTS_DIR / filename

        logger.info(f"Taking screenshot: {filepath}")
        self.page.screenshot(path=str(filepath), full_page=True)

        return str(filepath)

    def check_accessibility(self) -> dict:
        """
        Run basic accessibility checks

        Returns:
            Dict with accessibility check results
        """
        logger.info("Running accessibility checks")

        results = {
            "has_labels": False,
            "has_aria_attributes": False,
            "keyboard_navigable": False
        }

        # Check if input has label or aria-label
        try:
            aria_label = self.input_box.get_attribute("aria-label")
            placeholder = self.input_box.get_attribute("placeholder")
            results["has_labels"] = bool(aria_label or placeholder)
        except Exception:
            pass

        # Check for ARIA attributes
        try:
            role = self.message_container.get_attribute("role")
            results["has_aria_attributes"] = bool(role)
        except Exception:
            pass

        # Check if send button is keyboard accessible
        try:
            tab_index = self.send_button.get_attribute("tabindex")
            results["keyboard_navigable"] = tab_index is None or int(tab_index) >= 0
        except Exception:
            pass

        return results

    def wait_for_stable_response(self, timeout: int = 5000) -> None:
        """
        Wait for AI response to stop changing (fully rendered)

        Args:
            timeout: Maximum time to wait for stability
        """
        logger.info("Waiting for response to stabilize")

        previous_text = ""
        stable_count = 0
        max_checks = timeout // 500

        for _ in range(max_checks):
            current_text = self.get_last_ai_response()

            if current_text == previous_text and len(current_text) > 0:
                stable_count += 1
                if stable_count >= 3:  # 3 consecutive matches
                    logger.info("Response stabilized")
                    return
            else:
                stable_count = 0

            previous_text = current_text
            self.page.wait_for_timeout(500)

        logger.warning("Response did not stabilize within timeout")
