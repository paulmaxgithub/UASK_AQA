"""
Test automation helper functions with disclaimer and CAPTCHA handling
Can be imported in any framework tests
"""
import logging
import time
import allure
from typing import Dict, Any, Optional
from playwright.sync_api import Page, Locator

logger = logging.getLogger(__name__)


class AutomationHelpers:
    """Class with helper functions for test automation"""
    
    @staticmethod
    def close_disclaimer_reliably(page: Page, max_attempts: int = 3) -> bool:
        """
        Reliably closes disclaimer with multiple attempts
        
        Args:
            page: Playwright Page object
            max_attempts: Maximum number of attempts
            
        Returns:
            bool: True if disclaimer is closed or not found
        """
        disclaimer_selectors = [
            ".overlay-disclaimer button",
            ".disclaimer button",
            ".overlay button",
            "[data-dismiss='modal']",
            ".modal button",
            ".close-btn",
            "button:has-text('Close')",
            "button:has-text('Accept')",
            "button:has-text('Continue')",
            ".btn-close",
            "[aria-label*='close' i]",
            ".disclaimer-close",
            ".popup-close"
        ]
        
        for attempt in range(max_attempts):
            logger.info(f"Attempt {attempt + 1} to close disclaimer...")
            
            for selector in disclaimer_selectors:
                try:
                    disclaimer_btn = page.locator(selector).first
                    if disclaimer_btn.is_visible(timeout=2000):
                        logger.info(f"✓ Found disclaimer: {selector}")
                        disclaimer_btn.click()
                        time.sleep(2)
                        
                        # Check that disclaimer disappeared
                        if not disclaimer_btn.is_visible(timeout=2000):
                            logger.info("✓ Disclaimer successfully closed")
                            return True
                        
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
                    continue
            
            # Additional attempts
            try:
                page.keyboard.press("Escape")
                time.sleep(1)
            except:
                pass
            
            # Check overlay click
            try:
                overlay = page.locator(".overlay, .modal-backdrop").first
                if overlay.is_visible(timeout=1000):
                    overlay.click()
                    time.sleep(1)
            except:
                pass
            
            time.sleep(2)
        
        logger.info("Disclaimer not found or already closed")
        return True

    @staticmethod
    def close_captcha_modals(page: Page, max_attempts: int = 3) -> bool:
        """
        Closes CAPTCHA modal windows that block the interface
        
        Args:
            page: Playwright Page object
            max_attempts: Maximum number of attempts
            
        Returns:
            bool: True if modal windows are closed
        """
        modal_selectors = [
            "#modalRecaptcha",
            ".modal.show",
            ".swal2-container",
            ".modal-backdrop",
            "[role='dialog'][aria-modal='true']",
            ".captcha-modal",
            ".recaptcha-modal"
        ]
        
        close_selectors = [
            "#modalRecaptcha button",
            "#modalRecaptcha .btn-close",
            "#modalRecaptcha [aria-label*='close' i]",
            ".swal2-close",
            ".swal2-cancel",
            ".modal .close",
            ".modal .btn-close",
            ".modal button[data-dismiss='modal']",
            ".modal button:has-text('Close')",
            ".modal button:has-text('Cancel')",
            ".modal button:has-text('OK')"
        ]
        
        for attempt in range(max_attempts):
            logger.info(f"Attempt {attempt + 1} to close CAPTCHA modals...")
            
            # Check for modal windows
            modals_found = False
            for selector in modal_selectors:
                try:
                    modal = page.locator(selector).first
                    if modal.is_visible(timeout=2000):
                        logger.warning(f"🔍 Found modal window: {selector}")
                        modals_found = True
                        break
                except:
                    continue
            
            if not modals_found:
                logger.info("✓ CAPTCHA modal windows not found")
                return True
            
            # Try to close modal windows
            for selector in close_selectors:
                try:
                    close_btn = page.locator(selector).first
                    if close_btn.is_visible(timeout=2000):
                        logger.info(f"✓ Found close button: {selector}")
                        close_btn.click()
                        time.sleep(2)
                        
                        # Check that modal window disappeared
                        if not close_btn.is_visible(timeout=2000):
                            logger.info("✓ Modal window closed")
                            return True
                        
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
                    continue
            
            # Additional attempts
            try:
                # Press Escape
                page.keyboard.press("Escape")
                time.sleep(1)
                
                # Click on backdrop
                backdrop = page.locator(".modal-backdrop, .swal2-backdrop").first
                if backdrop.is_visible(timeout=1000):
                    backdrop.click()
                    time.sleep(1)
                    
            except:
                pass
            
            time.sleep(2)
        
        logger.warning("⚠️ CAPTCHA modal windows remain open")
        return False

    @staticmethod  
    def wait_for_services_to_load(page: Page, max_wait: int = 30) -> bool:
        """
        Waits for services to load
        
        Args:
            page: Playwright Page object
            max_wait: Maximum waiting time in seconds
            
        Returns:
            bool: True if services loaded
        """
        logger.info("Waiting for services to load...")
        
        loading_indicators = [
            "Connecting to Services...",
            "Loading...",
            "Please wait...",
            "Initializing...",
            "Loading...",
            "Connecting to services..."
        ]
        
        for i in range(max_wait):
            time.sleep(1)
            try:
                body_text = page.locator("body").inner_text()
                
                # Check that loading is completed
                is_loading = any(indicator in body_text for indicator in loading_indicators)
                
                if not is_loading:
                    logger.info(f"✓ Services loaded in {i+1} seconds!")
                    return True
                    
            except Exception as e:
                logger.debug(f"Error checking loading: {e}")
                
            if (i + 1) % 10 == 0:
                logger.info(f"Waiting for loading... {i+1}/{max_wait} seconds")
        
        logger.warning("Loading did not complete within the allotted time")
        return False

    @staticmethod
    def setup_page_reliably(page: Page, url: str = "https://ask.u.ae/en/") -> Dict[str, Any]:
        """
        Reliably prepares page for testing
        
        Args:
            page: Playwright Page object
            url: URL to load
            
        Returns:
            Dict with preparation results
        """
        logger.info("=== Page preparation ===")
        
        # Navigation
        logger.info(f"Opening website: {url}")
        page.goto(url, timeout=60000)
        time.sleep(3)
        
        # Screenshot initial state
        try:
            allure.attach(page.screenshot(full_page=True), name="Page Initial Load", attachment_type=allure.attachment_type.PNG)
        except:
            pass
        
        # Close disclaimer
        disclaimer_closed = AutomationHelpers.close_disclaimer_reliably(page)
        
        # Close CAPTCHA modal windows if any
        captcha_modals_closed = AutomationHelpers.close_captcha_modals(page)
        
        # Wait for services to load
        services_loaded = AutomationHelpers.wait_for_services_to_load(page, max_wait=30)
        
        # Check modal windows again after loading
        final_modals_closed = AutomationHelpers.close_captcha_modals(page)
        
        # Final screenshot
        try:
            allure.attach(page.screenshot(full_page=True), name="Page Ready", attachment_type=allure.attachment_type.PNG)
        except:
            pass
        
        result = {
            "disclaimer_closed": disclaimer_closed,
            "captcha_modals_closed": captcha_modals_closed,
            "services_loaded": services_loaded,
            "final_modals_closed": final_modals_closed,
            "page_ready": disclaimer_closed and services_loaded,
            "url": url,
            "title": page.title()
        }
        
        logger.info(f"Preparation result: {result}")
        return result

    @staticmethod
    def find_chat_elements(page: Page) -> Dict[str, Any]:
        """
        Reliably finds chat elements with fallback selectors
        
        Args:
            page: Playwright Page object
            
        Returns:
            Dict with found elements
        """
        
        # Selectors for input field
        input_selectors = [
            "[contenteditable='true'][placeholder*='ask' i]",
            "[contenteditable='true'][placeholder*='question' i]",
            "[contenteditable='true']:not([aria-hidden='true'])",
            "textarea[placeholder*='ask' i]",
            "textarea[placeholder*='question' i]",
            "input[placeholder*='ask' i]",
            ".chat-input textarea",
            ".chat-input input",
            ".message-input",
            "#chat-input",
            ".input-message"
        ]
        
        # Selectors for send button
        send_selectors = [
            "button[aria-label*='send' i]",
            "button[title*='send' i]",
            "button:has-text('Send')",
            ".send-button",
            ".chat-send",
            "button svg[class*='send']",
            "button:has(svg)",
            ".btn-send",
            "[data-testid*='send']",
            "button[type='submit']"
        ]
        
        # Selectors for chat widget
        widget_selectors = [
            "#chat-widget",
            ".chat-widget",
            "#chat-container", 
            ".chat-container",
            "iframe[title*='chat']",
            "[data-testid*='chat']",
            ".chat-wrapper",
            ".chatbot"
        ]
        
        result = {
            "input_box": None,
            "send_button": None,
            "chat_widget": None,
            "input_found": False,
            "send_found": False,
            "widget_found": False,
            "input_selector": None,
            "send_selector": None,
            "widget_selector": None
        }
        
        # Search for input field
        for selector in input_selectors:
            try:
                element = page.locator(selector).first
                if element.is_visible(timeout=3000):
                    logger.info(f"✓ Found input field: {selector}")
                    result["input_box"] = element
                    result["input_found"] = True
                    result["input_selector"] = selector
                    break
            except:
                continue
        
        # Search for send button
        for selector in send_selectors:
            try:
                element = page.locator(selector).first
                if element.is_visible(timeout=3000):
                    logger.info(f"✓ Found send button: {selector}")
                    result["send_button"] = element
                    result["send_found"] = True
                    result["send_selector"] = selector
                    break
            except:
                continue
        
        # Search for chat widget
        for selector in widget_selectors:
            try:
                element = page.locator(selector).first
                if element.count() > 0:  # May not be visible
                    logger.info(f"✓ Found chat widget: {selector}")
                    result["chat_widget"] = element
                    result["widget_found"] = True
                    result["widget_selector"] = selector
                    break
            except:
                continue
        
        logger.info(f"Found elements: input={result['input_found']}, send={result['send_found']}, widget={result['widget_found']}")
        return result

    @staticmethod
    def type_message_reliably(page: Page, message: str, input_element: Optional[Locator] = None) -> bool:
        """
        Reliably enters message into chat field
        
        Args:
            page: Playwright Page object
            message: message to enter
            input_element: Ready input field element (if None, searched automatically)
            
        Returns:
            bool: True if message entered successfully
        """
        if input_element is None:
            elements = AutomationHelpers.find_chat_elements(page)
            if not elements["input_found"]:
                logger.error("Input field not found")
                return False
            input_element = elements["input_box"]
        
        try:
            logger.info(f"Typing message: {message}")
            
            # Click on field
            input_element.click()
            time.sleep(0.5)
            
            # Clear field
            input_element.fill("")
            time.sleep(0.3)
            
            # Enter message
            input_element.fill(message)
            time.sleep(1)
            
            # Check that text is entered
            try:
                if "contenteditable" in str(input_element):
                    current_value = input_element.inner_text()
                else:
                    current_value = input_element.input_value()
                
                success = message in current_value
                if success:
                    logger.info(f"✓ Message successfully typed: {current_value[:50]}...")
                else:
                    logger.warning(f"Message not entered correctly. Expected: {message}, got: {current_value}")
                
                return success
                
            except Exception as e:
                logger.warning(f"Failed to verify entered text: {e}")
                return True  # Assume success if cannot verify
                
        except Exception as e:
            logger.error(f"Error entering message: {e}")
            return False

    @staticmethod
    def click_send_button_reliably(page: Page, send_element: Optional[Locator] = None) -> bool:
        """
        Reliably clicks the send button
        
        Args:
            page: Playwright Page object
            send_element: Ready send button element (if None, searched automatically)
            
        Returns:
            bool: True if button clicked successfully
        """
        if send_element is None:
            elements = AutomationHelpers.find_chat_elements(page)
            if not elements["send_found"]:
                logger.error("Send button not found")
                return False
            send_element = elements["send_button"]
        
        try:
            logger.info("Clicking send button...")
            send_element.click()
            time.sleep(1)
            logger.info("✓ Send button clicked")
            return True
            
        except Exception as e:
            logger.error(f"Error clicking send button: {e}")
            return False

    @staticmethod
    def check_for_captcha(page: Page) -> Dict[str, Any]:
        """
        Quickly checks for active CAPTCHA
        
        Args:
            page: Playwright Page object
            
        Returns:
            Dict with CAPTCHA information
        """
        captcha_results = {
            "captcha_detected": False,
            "captcha_types": []
        }
        
        # Main selectors for active CAPTCHA (only visible elements)
        captcha_selectors = [
            ("iframe[src*='recaptcha']:visible", "Active reCAPTCHA"),
            (".g-recaptcha:visible", "Visible Google reCAPTCHA"),
            ("#modalRecaptcha:visible", "CAPTCHA Modal")
        ]
        
        for selector, description in captcha_selectors:
            try:
                # Quick presence and visibility check
                elements = page.locator(selector)
                if elements.count() > 0:
                    # Additionally check visibility of first element
                    first_element = elements.first
                    if first_element.is_visible():
                        captcha_results["captcha_detected"] = True
                        captcha_results["captcha_types"].append(description)
                        logger.debug(f"🔍 Active CAPTCHA: {description}")
                        break  # Found active CAPTCHA, stop checking further
                        
            except Exception as e:
                logger.debug(f"Error checking {selector}: {e}")
                continue
        
        return captcha_results

    @staticmethod
    def wait_for_manual_captcha_solution(page: Page, timeout: int = 30) -> bool:
        """
        Notifies user about CAPTCHA and waits for its solution
        
        Args:
            page: Playwright Page object
            timeout: maximum waiting time in seconds (default 30)
            
        Returns:
            bool: True if CAPTCHA disappeared
        """
        print("\n" + "="*60)
        print("🔴 CAPTCHA detected - manual solution required")
        print("="*60)
        print("👆 Solve CAPTCHA in browser")
        print("⏳ Test will automatically continue when CAPTCHA disappears")
        print(f"⏰ Timeout: {timeout} seconds")
        print("="*60 + "\n")
        
        import time
        
        start_time = time.time()
        check_interval = 5  # Check every 5 seconds
        checks_made = 0
        
        while time.time() - start_time < timeout:
            checks_made += 1
            elapsed = int(time.time() - start_time)
            remaining = timeout - elapsed
            
            # Quick CAPTCHA check
            try:
                captcha_info = AutomationHelpers.check_for_captcha(page)
                if not captcha_info["captcha_detected"]:
                    logger.info(f"✅ CAPTCHA disappeared after {elapsed} seconds")
                    print(f"\n✅ CAPTCHA SOLVED! Continuing test...\n")
                    return True
                    
            except Exception as e:
                logger.debug(f"CAPTCHA check error: {e}")
            
            # Show progress only every second check (every 10s)
            if checks_made % 2 == 0:
                logger.info(f"🔍 Waiting for CAPTCHA solution... ( {remaining}s remaining)")
            
            # Wait before next check
            if remaining > check_interval:
                time.sleep(check_interval)
            else:
                time.sleep(remaining)
                break
        
        # Final check
        try:
            final_check = AutomationHelpers.check_for_captcha(page)
            if not final_check["captcha_detected"]:
                logger.info("✅ CAPTCHA solved at the last moment")
                print(f"\n✅ CAPTCHA SOLVED! Continuing test...\n")
                return True
            else:
                logger.warning(f"⏰ CAPTCHA not solved within {timeout} seconds")
                print(f"\n⏰ Time expired - continuing test\n")
                return False
        except Exception:
            print(f"\n⚠️ Continuing test\n")
            return False

    @staticmethod
    def send_message_complete(page: Page, message: str, wait_for_response: bool = True) -> Dict[str, Any]:
        """
        Complete message sending cycle: finds elements, enters text, sends, checks CAPTCHA
        
        Args:
            page: Playwright Page object
            message: Message to send
            wait_for_response: Whether to wait for bot response
            
        Returns:
            Dict with sending results
        """
        logger.info(f"=== Sending message: {message} ===")
        
        # Find chat elements
        elements = AutomationHelpers.find_chat_elements(page)
        
        if not elements["input_found"]:
            return {
                "success": False,
                "error": "Input field not found",
                "elements": elements
            }
        
        if not elements["send_found"]:
            return {
                "success": False,
                "error": "Send button not found", 
                "elements": elements
            }
        
        # Check CAPTCHA before sending
        captcha_before = AutomationHelpers.check_for_captcha(page)
        
        # Enter message
        typing_success = AutomationHelpers.type_message_reliably(page, message, elements["input_box"])
        if not typing_success:
            return {
                "success": False,
                "error": "Failed to enter message",
                "captcha_before": captcha_before,
                "elements": elements
            }
        
        # Screenshot with entered message
        try:
            allure.attach(page.screenshot(full_page=True), name="Message Typed", attachment_type=allure.attachment_type.PNG)
        except:
            pass
        
        # Send message
        send_success = AutomationHelpers.click_send_button_reliably(page, elements["send_button"])
        if not send_success:
            return {
                "success": False,
                "error": "Failed to click send button",
                "captcha_before": captcha_before,
                "typing_success": typing_success,
                "elements": elements
            }
        
        # Wait for system reaction
        time.sleep(2)  # Reduced waiting from 3 to 2 seconds
        
        # Quickly close CAPTCHA modal windows if they appear
        modal_close_success = AutomationHelpers.close_captcha_modals(page)
        
        # Quick CAPTCHA check after sending
        captcha_after = AutomationHelpers.check_for_captcha(page)
        
        # If CAPTCHA detected - notify user
        captcha_manually_solved = False
        if captcha_after["captcha_detected"]:
            logger.warning("🔴 CAPTCHA detected - manual solution required")
            captcha_manually_solved = AutomationHelpers.wait_for_manual_captcha_solution(page, timeout=30)
        
        # Check that message appeared on page
        body_text = page.locator("body").inner_text()
        message_appears = message in body_text
        
        # Screenshot after sending
        try:
            allure.attach(page.screenshot(full_page=True), name="After Send", attachment_type=allure.attachment_type.PNG)
        except:
            pass
        
        # Wait for possible response
        content_changed = False
        if wait_for_response and message_appears:
            logger.info("Waiting for possible bot response...")
            initial_length = len(body_text)
            time.sleep(5)
            
            new_body_text = page.locator("body").inner_text()
            content_changed = len(new_body_text) != initial_length
        
        result = {
            "success": True,
            "message": message,
            "elements": elements,
            "typing_success": typing_success,
            "send_success": send_success,
            "message_appears": message_appears,
            "captcha_triggered": captcha_after["captcha_detected"],
            "captcha_manually_solved": captcha_manually_solved,
            "content_changed": content_changed,
            "body_text_length": len(body_text)
        }
        
        logger.info(f"sending result: success={result['success']}, message_appears={message_appears}, captcha_triggered={result['captcha_triggered']}")
        
        return result

    @staticmethod
    def safe_screenshot(page: Page, name: str = "screenshot") -> bool:
        """
        Safely takes screenshot (doesn't crash on error)
        
        Args:
            page: Playwright Page object
            name: Screenshot name for Allure
            
        Returns:
            bool: True if screenshot taken successfully
        """
        try:
            allure.attach(page.screenshot(full_page=True), name=name, attachment_type=allure.attachment_type.PNG)
            return True
        except Exception as e:
            logger.warning(f"Failed to take screenshot {name}: {e}")
            return False

    @staticmethod
    def log_test_results(results: Dict[str, Any], test_name: str = "Test") -> None:
        """
        Logs test results to Allure
        
        Args:
            results: Dictionary with results
            test_name: Test name
        """
        try:
            results_text = f"""
{test_name} Results:
{chr(10).join([f'- {key}: {value}' for key, value in results.items()])}
            """
            allure.attach(results_text, name=f"{test_name} Results", attachment_type=allure.attachment_type.TEXT)
        except Exception as e:
            logger.warning(f"Failed to save results to Allure: {e}")


# Alias for convenient import
RTH = AutomationHelpers
