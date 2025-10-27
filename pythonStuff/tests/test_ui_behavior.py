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
        logger.info("=== ТЕСТ: Загрузка виджета чата на десктопе ===")
        
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()
        
        # Надежная подготовка страницы
        setup_result = AutomationHelpers.setup_page_reliably(page)
        assert setup_result["page_ready"], "Страница не готова к тестированию"
        
        # Поиск элементов чата с fallback
        elements = AutomationHelpers.find_chat_elements(page)
        
        assert elements["input_found"], "Поле ввода не найдено"
        assert elements["send_found"], "Кнопка отправки не найдена"
        assert elements["widget_found"], "Виджет чата не найден"
        
        logger.info(f"Найденные элементы: input={elements['input_found']}, send={elements['send_found']}, widget={elements['widget_found']}")
        
        # Проверяем CAPTCHA (документируем, но не блокируем)
        captcha_info = AutomationHelpers.check_for_captcha(page)
        if captcha_info["captcha_detected"]:
            logger.warning(f"🔍 CAPTCHA обнаружена: {captcha_info}")
        
        logger.info("✅ Тест загрузки виджета на десктопе пройден")
        
        context.close()

    @pytest.mark.mobile
    @allure.title("Chat widget loads correctly on mobile")  
    def test_mobile_simulation(self, browser):
        """Verify chat widget loads correctly on mobile"""
        logger.info("=== ТЕСТ: Имитация мобильного виджета ===")
        
        # Мобильный viewport
        context = browser.new_context(viewport={'width': 375, 'height': 667})
        page = context.new_page()
        
        setup_result = AutomationHelpers.setup_page_reliably(page)
        assert setup_result["page_ready"], "Мобильная страница не готова"
        
        elements = AutomationHelpers.find_chat_elements(page)
        
        assert elements["input_found"], "Мобильное поле ввода не найдено"
        assert elements["send_found"], "Мобильная кнопка отправки не найдена"
        assert elements["widget_found"], "Мобильный виджет чата не найден"
        
        logger.info(f"Найденные элементы: input={elements['input_found']}, send={elements['send_found']}, widget={elements['widget_found']}")
        
        logger.info("✅ Тест мобильной имитации пройден")
        
        context.close()


@pytest.mark.ui
class TestMessageSending:
    """Test message sending functionality"""

    @allure.title("User can type message in input box")
    def test_user_can_type_message(self, browser):
        """Verify user can type a message in input box"""
        logger.info("=== ТЕСТ: Ввод сообщения пользователем ===")
        
        context = browser.new_context()
        page = context.new_page()
        
        setup_result = AutomationHelpers.setup_page_reliably(page)
        assert setup_result["page_ready"], "Страница не готова"
        
        elements = AutomationHelpers.find_chat_elements(page)
        assert elements["input_found"], "Поле ввода не найдено"
        
        test_message = "Hello, how can I apply for a visa?"
        
        # Надежный ввод сообщения
        typing_success = AutomationHelpers.type_message_reliably(page, test_message, elements["input_box"])
        assert typing_success, "Не удалось ввести сообщение"
        
        logger.info(f"Вводим сообщение: {test_message}")
        logger.info("✅ Тест ввода сообщения пройден")
        
        context.close()

    @allure.title("Send button interaction works correctly")
    def test_send_button_interaction(self, browser):
        """Verify send button can be clicked"""
        logger.info("=== ТЕСТ: Взаимодействие с кнопкой отправки ===")
        
        context = browser.new_context()
        page = context.new_page()
        
        setup_result = AutomationHelpers.setup_page_reliably(page)
        assert setup_result["page_ready"], "Страница не готова"
        
        elements = AutomationHelpers.find_chat_elements(page)
        
        # Проверяем CAPTCHA до отправки
        captcha_before = AutomationHelpers.check_for_captcha(page)
        if captcha_before["captcha_detected"]:
            logger.warning(f"🔍 CAPTCHA найдена: {captcha_before}")
        
        # Кликаем кнопку отправки
        logger.info("Нажимаем кнопку отправки...")
        send_success = AutomationHelpers.click_send_button_reliably(page, elements["send_button"])
        assert send_success, "Не удалось нажать кнопку отправки"
        
        # Проверяем CAPTCHA после отправки  
        captcha_after = AutomationHelpers.check_for_captcha(page)
        if captcha_after["captcha_detected"]:
            logger.warning("⚠️ CAPTCHA обнаружена после отправки - это ожидаемо")
        
        logger.info("✅ Тест кнопки отправки пройден")
        
        context.close()


@pytest.mark.ui
class TestUIResponsiveness:
    """Test UI responsiveness and behavior"""

    @allure.title("Page elements are visible and accessible")
    def test_page_elements_are_visible(self, browser):
        """Verify all key page elements are visible"""
        logger.info("=== ТЕСТ: Видимость элементов страницы ===")
        
        context = browser.new_context()
        page = context.new_page()
        
        setup_result = AutomationHelpers.setup_page_reliably(page)
        assert setup_result["page_ready"], "Страница не готова"
        
        elements = AutomationHelpers.find_chat_elements(page)
        
        assert elements["input_found"], "Поле ввода не видно"
        assert elements["send_found"], "Кнопка отправки не видна"
        assert elements["widget_found"], "Виджет чата не виден"
        
        logger.info(f"Найденные элементы: input={elements['input_found']}, send={elements['send_found']}, widget={elements['widget_found']}")
        logger.info("✅ Тест видимости элементов пройден")
        
        context.close()

    @allure.title("Language and text direction detection")
    def test_language_and_direction_detection(self, browser):
        """Test language and text direction"""
        logger.info("=== ТЕСТ: Определение языка и направления текста ===")
        
        context = browser.new_context()
        page = context.new_page()
        
        setup_result = AutomationHelpers.setup_page_reliably(page)
        assert setup_result["page_ready"], "Страница не готова"
        
        # Получаем информацию о языке страницы
        try:
            lang = page.locator("html").get_attribute("lang") or "en"
            dir_attr = page.locator("html").get_attribute("dir") or "ltr"
            
            logger.info(f"Язык страницы: {lang}, направление: {dir_attr}")
            
            # Для английского ожидаем LTR
            if "en" in lang.lower():
                assert dir_attr == "ltr" or dir_attr is None, f"Для английского ожидается LTR, получили: {dir_attr}"
            
        except Exception as e:
            logger.warning(f"Не удалось определить язык/направление: {e}")
        
        logger.info("✅ Тест определения языка пройден")
        
        context.close()


@pytest.mark.ui  
class TestErrorHandlingAndEdgeCases:
    """Test error handling and edge cases"""

    @allure.title("Empty message handling")
    def test_empty_message_handling(self, browser):
        """Test how system handles empty messages"""
        logger.info("=== ТЕСТ: Обработка пустых сообщений ===")
        
        context = browser.new_context()
        page = context.new_page()
        
        setup_result = AutomationHelpers.setup_page_reliably(page)
        assert setup_result["page_ready"], "Страница не готова"
        
        elements = AutomationHelpers.find_chat_elements(page)
        
        # Пробуем отправить пустое сообщение
        logger.info("Пробуем отправить пустое сообщение...")
        try:
            elements["input_box"].fill("")
            send_success = AutomationHelpers.click_send_button_reliably(page, elements["send_button"])
            logger.info(f"Пустое сообщение отправлено: {send_success}")
        except Exception as e:
            logger.info(f"Пустое сообщение обработано с исключением: {e}")
        
        logger.info("✅ Тест обработки пустых сообщений пройден")
        
        context.close()

    @allure.title("Page responsiveness under load")
    def test_page_responsiveness_under_load(self, browser):
        """Test page responsiveness under multiple actions"""
        logger.info("=== ТЕСТ: Отзывчивость страницы под нагрузкой ===")
        
        context = browser.new_context()
        page = context.new_page()
        
        setup_result = AutomationHelpers.setup_page_reliably(page)
        assert setup_result["page_ready"], "Страница не готова"
        
        elements = AutomationHelpers.find_chat_elements(page)
        
        # Выполняем множественные действия
        logger.info("Выполняем множественные действия...")
        for i in range(3):
            try:
                elements["input_box"].fill(f"Test message {i}")
                page.wait_for_timeout(500)
                elements["input_box"].clear()
                page.wait_for_timeout(500)
            except Exception as e:
                logger.warning(f"Действие {i} вызвало исключение: {e}")
        
        # Страница должна оставаться отзывчивой
        final_elements = AutomationHelpers.find_chat_elements(page)
        assert final_elements["input_found"], "Поле ввода стало недоступно после нагрузки"
        
        logger.info("✅ Тест отзывчивости под нагрузкой пройден")
        
        context.close()
