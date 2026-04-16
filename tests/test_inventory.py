"""
test_inventory.py
-----------------
Test suite for the Inventory module — covers page title,
product count, all four sort orders with list-comparison
assertions, and cart badge management (add/remove).
"""
import pytest
from config.config_reader import STANDARD_USER, PASSWORD
from pages.login_page import Login_page
from pages.inventory_page import Inventory_page
from utils.logger import get_logger

logger = get_logger(__name__)


@pytest.mark.usefixtures("setup")
class TestInventory:
    """Inventory page test suite."""

    @pytest.fixture(autouse=True)
    def initialise_pages(self, setup):
        """Log in as standard_user before each test."""
        self.login_page = Login_page(self.driver)
        self.inventory_page = Inventory_page(self.driver)
        self.login_page.login(STANDARD_USER, PASSWORD)

    # ── Page state ───────────────────────────────────────────────────────────

    def test_page_title_is_products(self):
        """Inventory page header reads 'Products' after login."""
        page_title = self.inventory_page.get_page_title()
        assert page_title == "Products", (
            f"Expected page title 'Products', got '{page_title}'"
        )
        logger.info("PASS — inventory page title is 'Products'.")

    def test_product_count_is_six(self):
        """Exactly 6 product cards are displayed on the inventory page."""
        product_count = self.inventory_page.get_product_option()
        assert product_count == 6, (
            f"Expected 6 products, found {product_count}."
        )
        logger.info("PASS — inventory displays 6 products.")

    # ── Sort validation ──────────────────────────────────────────────────────

    def test_sort_name_a_to_z(self):
        """Products sort A→Z — validated by comparing list to sorted(list)."""
        self.inventory_page.sort_by("az")
        names = self.inventory_page.get_all_products_names()
        assert names == sorted(names), (
            f"Sort A→Z failed. Actual order: {names}"
        )
        logger.info("PASS — sort A→Z produces correct ascending order.")

    def test_sort_name_z_to_a(self):
        """Products sort Z→A — validated by comparing list to sorted(list, reverse=True)."""
        self.inventory_page.sort_by("za")
        names = self.inventory_page.get_all_products_names()
        assert names == sorted(names, reverse=True), (
            f"Sort Z→A failed. Actual order: {names}"
        )
        logger.info("PASS — sort Z→A produces correct descending order.")

    def test_sort_price_low_to_high(self):
        """Products sort price low→high — validated against sorted float list."""
        self.inventory_page.sort_by("lohi")
        prices = self._get_prices_as_floats()
        assert prices == sorted(prices), (
            f"Sort price low→high failed. Actual prices: {prices}"
        )
        logger.info("PASS — sort price low→high produces correct ascending order.")

    def test_sort_price_high_to_low(self):
        """Products sort price high→low — validated against reverse-sorted float list."""
        self.inventory_page.sort_by("hilo")
        prices = self._get_prices_as_floats()
        assert prices == sorted(prices, reverse=True), (
            f"Sort price high→low failed. Actual prices: {prices}"
        )
        logger.info("PASS — sort price high→low produces correct descending order.")

    # ── Cart badge ───────────────────────────────────────────────────────────

    def test_add_single_item_updates_cart_badge(self):
        """Adding one item increments the cart badge to 1."""
        self.inventory_page.add_to_cart_by_name("Sauce Labs Backpack")
        cart_count = self.inventory_page.get_cart_count()
        assert cart_count == 1, (
            f"Cart badge expected 1, got {cart_count}."
        )
        logger.info("PASS — cart badge shows 1 after adding one item.")

    def test_add_multiple_items_updates_cart_badge(self):
        """Adding three items increments the cart badge to 3."""
        self.inventory_page.add_to_cart_by_name("Sauce Labs Backpack")
        self.inventory_page.add_to_cart_by_name("Sauce Labs Bike Light")
        self.inventory_page.add_to_cart_by_name("Sauce Labs Fleece Jacket")
        cart_count = self.inventory_page.get_cart_count()
        assert cart_count == 3, (
            f"Cart badge expected 3, got {cart_count}."
        )
        logger.info("PASS — cart badge shows 3 after adding three items.")

    def test_remove_item_from_inventory_updates_cart_badge(self):
        """Removing an item from the inventory page decrements the cart badge to 0."""
        self.inventory_page.add_to_cart_by_name("Sauce Labs Backpack")
        self.inventory_page.remove_by_name("Sauce Labs Backpack")
        cart_count = self.inventory_page.get_cart_count()
        assert cart_count == 0, (
            f"Cart badge expected 0 after removal, got {cart_count}."
        )
        logger.info("PASS — cart badge returns to 0 after removing item.")

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _get_prices_as_floats(self):
        """Strip $ prefix from price strings and return as a list of floats."""
        prices = self.inventory_page.get_all_product_prices()
        return [float(price.strip("$")) for price in prices]