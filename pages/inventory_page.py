"""
inventory_page.py
Page Object for /inventory.html — the main product listing page.
Covers product retrieval, sort validation, and cart interaction.
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from pages.base_page import BasePage
from utils.logger import get_logger

logger = get_logger(__name__)


class InventoryPage(BasePage):
    """
    Page Object for /inventory.html — the main product listing page.
    Covers product retrieval, sort validation, and cart interaction.
    """

    # ── Locators — CSS Selectors ───────────────────────────────────────────────
    _PAGE_TITLE_FIELD         = ".title"
    _ALL_PRODUCTS_NAME_FIELD  = ".inventory_item_name"
    _ALL_PRODUCTS_PRICE_FIELD = ".inventory_item_price"
    _PRODUCT_CARD             = ".inventory_item"
    _SORT_DROPDOWN            = "select.product_sort_container"
    _ADD_TO_CART_BUTTONS      = "div[class='pricebar']>button"
    _SHOPPING_CART_BADGE      = ".shopping_cart_badge"
    _SHOPPING_CART_ICON       = "div[id='shopping_cart_container']"

    def _get_add_to_cart_locator(self, name):
        return (By.XPATH, f'//div[text()="{name}"]/ancestor::div[@class="inventory_item"]//div[@class="pricebar"]//button[text()="Add to cart"]')

    def _get_remove_from_cart_locator(self, name):
        return (By.XPATH, f'//div[text()="{name}"]/ancestor::div[@class="inventory_item"]//div[@class="pricebar"]//button[text()="Remove"]')

    def __init__(self, driver):
        super().__init__(driver)

    def get_page_title(self):
        return self.get_text((By.CSS_SELECTOR, self._PAGE_TITLE_FIELD))

    def get_all_products_names(self):
        elements = self.wait_and_find_elements((By.CSS_SELECTOR, self._ALL_PRODUCTS_NAME_FIELD))
        return [el.text.strip() for el in elements]

    def get_all_product_prices(self):
        elements = self.wait_and_find_elements((By.CSS_SELECTOR, self._ALL_PRODUCTS_PRICE_FIELD))
        return [price.text.strip() for price in elements]

    def get_product_count(self):
        elements = self.wait_and_find_elements((By.CSS_SELECTOR, self._PRODUCT_CARD))
        return len(elements)

    def sort_by(self, option):
        logger.info("Sorting products by: %s", option)
        valid_options = ["az", "za", "lohi", "hilo"]
        if option not in valid_options:
            raise ValueError(f"Invalid sort option '{option}'. Valid options: {valid_options}")
        dropdown = self.wait_and_find_element((By.CSS_SELECTOR, self._SORT_DROPDOWN))
        Select(dropdown).select_by_value(option)

    def add_to_cart_by_index(self, index):
        buttons = self.wait_and_find_elements((By.CSS_SELECTOR, self._ADD_TO_CART_BUTTONS))
        buttons[index].click()

    def add_to_cart_by_name(self, name):
        logger.info("Adding to cart: %s", name)
        self.click_element(self._get_add_to_cart_locator(name))

    def remove_by_name(self, name):
        logger.info("Removing from cart: %s", name)
        self.click_element(self._get_remove_from_cart_locator(name))

    def get_cart_count(self):
        try:
            return int(self.get_text((By.CSS_SELECTOR, self._SHOPPING_CART_BADGE), timeout=4))
        except Exception:
            return 0  # Badge is absent — cart is empty

    def go_to_cart(self):
        self.click_element((By.CSS_SELECTOR, self._SHOPPING_CART_ICON))
        from pages.cart_page import CartPage
        return CartPage(self.driver)