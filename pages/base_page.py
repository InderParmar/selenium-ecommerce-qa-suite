"""
base_page.py
Abstract base class for all Page Objects. Wraps Selenium interactions
behind explicit-wait methods — no test ever touches the driver directly.
"""

from config.config_reader import EXPLICIT_WAIT
from utils import wait_helper
from utils.logger import get_logger

logger = get_logger(__name__)


class BasePage:
    """
    Base class providing shared WebDriver utility methods.
    All page classes inherit from this.
    """

    def __init__(self, driver):
        self.driver = driver

    def click_element(self, locator, timeout=EXPLICIT_WAIT):
        logger.debug("Clicking element | locator: %s", locator[1])
        element = wait_helper.wait_until_element_is_clickable(self.driver, locator, timeout)
        element.click()

    def enter_text(self, locator, text, timeout=EXPLICIT_WAIT):
        logger.debug("Entering text | locator: %s | value: %s", locator[1], text)
        element = wait_helper.wait_until_element_is_visible(self.driver, locator, timeout)
        element.send_keys(text)

    def get_text(self, locator, timeout=EXPLICIT_WAIT):
        element = wait_helper.wait_until_element_is_visible(self.driver, locator, timeout)
        return element.text

    def get_attribute(self, locator, attr, timeout=EXPLICIT_WAIT):
        element = wait_helper.wait_until_element_is_visible(self.driver, locator, timeout)
        return element.get_attribute(attr)

    def is_element_visible(self, locator, timeout=EXPLICIT_WAIT):
        try:
            wait_helper.wait_until_element_is_visible(self.driver, locator, timeout)
            return True
        except Exception:
            return False

    def wait_and_find_elements(self, locator, timeout=EXPLICIT_WAIT):
        return wait_helper.wait_for_presence_of_all_elements_located(self.driver, locator, timeout)

    def scroll_into_view_center(self, locator, timeout=EXPLICIT_WAIT):
        element = wait_helper.wait_until_element_is_present(self.driver, locator, timeout)
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)

    def scroll_into_view_top(self, locator, timeout=EXPLICIT_WAIT):
        element = wait_helper.wait_until_element_is_present(self.driver, locator, timeout)
        self.driver.execute_script("arguments[0].scrollIntoView();", element)

    def clear_and_enter_text(self, locator, text, timeout=EXPLICIT_WAIT):
        element = wait_helper.wait_until_element_is_visible(self.driver, locator, timeout)
        element.clear()
        element.send_keys(text)

    def wait_and_find_element(self, locator, timeout=EXPLICIT_WAIT, parent=None):
        """Finds a single element, optionally scoped to a parent WebElement."""
        search_context = parent if parent else self.driver
        return wait_helper.wait_until_element_is_present(search_context, locator, timeout)