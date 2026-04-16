"""
cart_page.py
Page Object for /cart.html.
Validates cart contents, item prices, and navigates to Checkout or back to Inventory.
"""

from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from utils.logger import get_logger

logger = get_logger(__name__)


class CartPage(BasePage):
    """
    Page Object for /cart.html.
    Validates cart contents, item prices, and navigates to Checkout or back to Inventory.
    """

    # ── Locators — CSS Selectors ───────────────────────────────────────────────
    _CART_ITEM_CONTAINER = "div.cart_item"
    _CART_ITEM_NAME      = "div.inventory_item_name"
    _CART_ITEM_PRICE     = "div.inventory_item_price"
    _CONTINUE_SHOPPING   = "button#continue-shopping"
    _CHECKOUT_BUTTON     = "button#checkout"

    def __init__(self, driver):
        super().__init__(driver)

    def _get_remove_from_cart_locator_by_name(self, name):
        return (By.XPATH, f'//div[text()="{name}"]/ancestor::div[@class="cart_item"]//div[@class="item_pricebar"]//button[text()="Remove"]')

    def get_cart_items(self):
        return self.wait_and_find_elements((By.CSS_SELECTOR, self._CART_ITEM_CONTAINER))

    def get_item_names(self):
        elements = self.wait_and_find_elements((By.CSS_SELECTOR, self._CART_ITEM_NAME))
        return [el.text for el in elements]

    def get_item_prices(self):
        elements = self.wait_and_find_elements((By.CSS_SELECTOR, self._CART_ITEM_PRICE))
        return [el.text for el in elements]

    def get_price_by_name(self, product_name):
        """Returns the price string for the given product. Raises ValueError if not found."""
        items = self.get_cart_items()
        for item in items:
            name_element = self.wait_and_find_element(
                (By.CSS_SELECTOR, self._CART_ITEM_NAME), parent=item
            )
            if name_element.text == product_name:
                price = self.wait_and_find_element(
                    (By.CSS_SELECTOR, self._CART_ITEM_PRICE), parent=item
                )
                return price.text
        logger.error(
            "Product '%s' not found in cart. Items present: %s",
            product_name, self.get_item_names()
        )
        raise ValueError(f"Product '{product_name}' not found in cart")

    def get_item_count(self):
        return len(self.get_cart_items())

    def remove_item_by_name(self, name):
        logger.info("Removing item from cart: %s", name)
        self.click_element(self._get_remove_from_cart_locator_by_name(name))

    def continue_shopping(self):
        self.click_element((By.CSS_SELECTOR, self._CONTINUE_SHOPPING))
        from pages.inventory_page import InventoryPage
        return InventoryPage(self.driver)

    def proceed_to_checkout(self):
        self.click_element((By.CSS_SELECTOR, self._CHECKOUT_BUTTON))
        from pages.checkout_page import CheckoutPage
        return CheckoutPage(self.driver)