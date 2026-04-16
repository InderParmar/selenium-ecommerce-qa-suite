"""
checkout_page.py
Page Object for /checkout-step-one.html and /checkout-step-two.html.
Handles form entry, field validation errors, and order total verification.
"""

from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from utils.logger import get_logger

logger = get_logger(__name__)


class CheckoutPage(BasePage):
    """
    Page Object for /checkout-step-one.html and /checkout-step-two.html.
    Handles form entry, field validation errors, and order total verification.
    """

    # ── Locators — CSS Selectors ───────────────────────────────────────────────
    _FIRST_NAME_FIELD     = "input#first-name"
    _LAST_NAME_FIELD      = "input#last-name"
    _POSTAL_CODE_FIELD    = "input#postal-code"
    _CONTINUE_BUTTON      = "input#continue"
    _ERROR_MESSAGE_TEXT   = "h3[data-test='error']"
    _DISMISS_ERROR_BUTTON = ".error-button"
    _SUBTOTAL_FIELD       = "div.summary_subtotal_label"
    _TAX_FIELD            = "div.summary_tax_label"
    _TOTAL_FIELD          = "div.summary_total_label"
    _FINISH_BUTTON        = "button#finish"
    _CONFIRMATION_HEADER  = "h2.complete-header"
    _BACK_HOME_BUTTON     = "button#back-to-products"

    def __init__(self, driver):
        super().__init__(driver)

    # ── Private helpers ────────────────────────────────────────────────────────

    def _parse_dollar_amount(self, locator) -> float:
        """Extracts and returns the float value from a '$X.XX' price label."""
        text = self.get_text((By.CSS_SELECTOR, locator))
        return float(text[text.find("$") + 1:])

    # ── Form entry ─────────────────────────────────────────────────────────────

    def enter_first_name(self, first_name):
        self.enter_text((By.CSS_SELECTOR, self._FIRST_NAME_FIELD), first_name)

    def enter_last_name(self, last_name):
        self.enter_text((By.CSS_SELECTOR, self._LAST_NAME_FIELD), last_name)

    def enter_postal_code(self, postal_code):
        self.enter_text((By.CSS_SELECTOR, self._POSTAL_CODE_FIELD), postal_code)

    def fill_checkout_info(self, first, last, postal_code):
        logger.info("Filling checkout info | name: %s %s | zip: %s", first, last, postal_code)
        self.enter_first_name(first)
        self.enter_last_name(last)
        self.enter_postal_code(postal_code)

    def click_continue(self):
        self.click_element((By.CSS_SELECTOR, self._CONTINUE_BUTTON))

    # ── Error state ────────────────────────────────────────────────────────────

    def get_error_message(self):
        return self.get_text((By.CSS_SELECTOR, self._ERROR_MESSAGE_TEXT))

    def is_error_displayed(self):
        return self.is_element_visible((By.CSS_SELECTOR, self._ERROR_MESSAGE_TEXT), 5)

    # ── Order summary ──────────────────────────────────────────────────────────

    def get_item_total(self) -> float:
        return self._parse_dollar_amount(self._SUBTOTAL_FIELD)

    def get_tax(self) -> float:
        return self._parse_dollar_amount(self._TAX_FIELD)

    def get_total(self) -> float:
        return self._parse_dollar_amount(self._TOTAL_FIELD)

    # ── Confirmation ───────────────────────────────────────────────────────────

    def click_finish(self):
        self.click_element((By.CSS_SELECTOR, self._FINISH_BUTTON))

    def get_confirmation_message(self):
        return self.get_text((By.CSS_SELECTOR, self._CONFIRMATION_HEADER))

    def is_order_confirmed(self) -> bool:
        return self.get_confirmation_message() == "Thank you for your order!"

    def click_back_home(self):
        self.click_element((By.CSS_SELECTOR, self._BACK_HOME_BUTTON))
        from pages.inventory_page import InventoryPage
        return InventoryPage(self.driver)