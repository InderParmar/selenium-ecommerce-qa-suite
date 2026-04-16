"""
login_page.py
Page Object for the Sauce Demo login screen (/).
Handles credential entry, login submission, and error state validation.
"""

from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from utils.logger import get_logger

logger = get_logger(__name__)


class LoginPage(BasePage):
    """
    Page Object for https://www.saucedemo.com (login screen).
    Handles credential entry, login submission, and error state validation.
    """

    # ── Locators — CSS Selectors ───────────────────────────────────────────────
    _USERNAME_FIELD       = "#user-name"
    _PASSWORD_FIELD       = "#password"
    _LOGIN_BUTTON         = "#login-button"
    _ERROR_MESSAGE_TEXT   = "h3[data-test='error']"
    _DISMISS_ERROR_BUTTON = ".error-button"

    def __init__(self, driver):
        super().__init__(driver)

    def enter_username(self, username):
        self.enter_text((By.CSS_SELECTOR, self._USERNAME_FIELD), username)

    def enter_password(self, password):
        self.enter_text((By.CSS_SELECTOR, self._PASSWORD_FIELD), password)

    def click_login(self):
        self.click_element((By.CSS_SELECTOR, self._LOGIN_BUTTON))

    def login(self, username, password):
        logger.info("Attempting login | user: %s", username)
        self.enter_username(username)
        self.enter_password(password)
        self.click_login()

    def get_error_message(self):
        return self.get_text((By.CSS_SELECTOR, self._ERROR_MESSAGE_TEXT))

    def is_error_displayed(self):
        return self.is_element_visible((By.CSS_SELECTOR, self._ERROR_MESSAGE_TEXT), 5)

    def dismiss_error(self):
        self.click_element((By.CSS_SELECTOR, self._DISMISS_ERROR_BUTTON))

    def is_login_page(self):
        return self.is_element_visible((By.CSS_SELECTOR, self._LOGIN_BUTTON), 5)