"""
wait_helper.py
Explicit-wait utility functions wrapping Selenium's WebDriverWait.
All waits are centralised here — no time.sleep() anywhere in the framework.
"""

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config.config_reader import EXPLICIT_WAIT
from utils.logger import get_logger

logger = get_logger(__name__)


def wait_until_element_is_visible(driver, locator, timeout=EXPLICIT_WAIT):
    logger.debug("Waiting for visible element  | locator: %s", locator[1])
    element = WebDriverWait(driver, timeout).until(EC.visibility_of_element_located(locator))
    logger.debug("Element is visible           | locator: %s", locator[1])
    return element


def wait_until_element_is_present(driver, locator, timeout=EXPLICIT_WAIT):
    logger.debug("Waiting for element presence | locator: %s", locator[1])
    element = WebDriverWait(driver, timeout).until(EC.presence_of_element_located(locator))
    logger.debug("Element is present           | locator: %s", locator[1])
    return element


def wait_until_element_is_clickable(driver, locator, timeout=EXPLICIT_WAIT):
    logger.debug("Waiting for clickable element | locator: %s", locator[1])
    element = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(locator))
    logger.debug("Element is clickable          | locator: %s", locator[1])
    return element


def wait_for_presence_of_all_elements_located(driver, locator, timeout=EXPLICIT_WAIT):
    logger.debug("Waiting for all elements | locator: %s", locator[1])
    elements = WebDriverWait(driver, timeout).until(EC.presence_of_all_elements_located(locator))
    logger.debug("Found %d element(s)      | locator: %s", len(elements), locator[1])
    return elements


def wait_for_url_contains(driver, url_substring, timeout=EXPLICIT_WAIT):
    """Waits until the current URL contains the specified substring. Returns False on timeout."""
    try:
        logger.debug("Waiting for URL to contain: %s", url_substring)
        result = WebDriverWait(driver, timeout).until(EC.url_contains(url_substring))
        logger.debug("URL confirmed to contain:   %s", url_substring)
        return result
    except Exception:
        # Swallow TimeoutException — caller receives False and decides how to handle it
        return False


def wait_for_text_present_in_element(driver, locator, text, timeout=EXPLICIT_WAIT):
    """Waits until the given element contains the expected text. Returns True when confirmed."""
    logger.debug("Waiting for text in element | locator: %s | expected: '%s'", locator[1], text)
    result = WebDriverWait(driver, timeout).until(
        EC.text_to_be_present_in_element(locator, text)
    )
    if result:
        logger.debug("Text confirmed in element   | text: '%s'", text)
    return result