"""
test_cart.py
------------
Test suite for the Cart module — covers item display accuracy,
count validation, price consistency between inventory and cart,
item removal, and navigation actions (continue shopping, checkout).
"""
import pytest
from config.config_reader import STANDARD_USER, PASSWORD
from utils import wait_helper
from pages.login_page import Login_page
from pages.inventory_page import Inventory_page
from utils.logger import get_logger

logger = get_logger(__name__)


@pytest.mark.usefixtures("setup")
class TestCart:
    """Cart page test suite."""

    @pytest.fixture(autouse=True)
    def initialise_pages(self, setup):
        """Log in as standard_user before each test.
        Cart state is set up inside individual tests — not shared."""
        self.login_page = Login_page(self.driver)
        self.inventory_page = Inventory_page(self.driver)
        self.login_page.login(STANDARD_USER, PASSWORD)

    # ── Item display ─────────────────────────────────────────────────────────

    def test_cart_displays_correct_item_names(self):
        """Items added by name appear in the cart with matching names."""
        items_to_add = ["Sauce Labs Backpack", "Sauce Labs Bike Light"]
        self.inventory_page.add_to_cart_by_name(items_to_add[0])
        self.inventory_page.add_to_cart_by_name(items_to_add[1])
        cart_page = self.inventory_page.go_to_cart()
        cart_item_names = cart_page.get_item_names()
        assert items_to_add == cart_item_names, (
            f"Cart contents mismatch. Added: {items_to_add}, "
            f"Found in cart: {cart_item_names}"
        )
        logger.info("PASS — cart displays correct item names.")

    def test_cart_item_count_matches_items_added(self):
        """Cart item count matches the number of items added from inventory."""
        self.inventory_page.add_to_cart_by_index(1)
        self.inventory_page.add_to_cart_by_index(2)
        cart_page = self.inventory_page.go_to_cart()
        cart_count = cart_page.get_item_count()
        assert cart_count == 2, (
            f"Expected 2 items in cart, found {cart_count}."
        )
        logger.info("PASS — cart item count matches items added.")

    # ── Price consistency ────────────────────────────────────────────────────

    def test_cart_price_matches_inventory_price(self):
        """Item price displayed in cart matches the price shown on inventory page."""
        all_prices = self.inventory_page.get_all_product_prices()
        all_names = self.inventory_page.get_all_products_names()
        product_name = "Sauce Labs Backpack"
        inventory_price = all_prices[all_names.index(product_name)]

        self.inventory_page.add_to_cart_by_name(product_name)
        cart_page = self.inventory_page.go_to_cart()
        cart_price = cart_page.get_price_by_name(product_name)

        assert inventory_price == cart_price, (
            f"Price mismatch for '{product_name}': "
            f"inventory shows {inventory_price}, cart shows {cart_price}."
        )
        logger.info(
            "PASS — cart price matches inventory price for '%s': %s",
            product_name, cart_price
        )

    # ── Remove item ──────────────────────────────────────────────────────────

    def test_remove_item_from_cart(self):
        """Removing one item from a two-item cart leaves exactly one item,
        and the removed item no longer appears in the cart."""
        items_to_add = ["Sauce Labs Backpack", "Sauce Labs Bike Light"]
        self.inventory_page.add_to_cart_by_name(items_to_add[0])
        self.inventory_page.add_to_cart_by_name(items_to_add[1])
        cart_page = self.inventory_page.go_to_cart()

        cart_page.remove_item_by_name("Sauce Labs Backpack")

        assert cart_page.get_item_count() == 1, (
            f"Expected 1 item after removal, found {cart_page.get_item_count()}."
        )
        assert "Sauce Labs Backpack" not in cart_page.get_item_names(), (
            "Removed item 'Sauce Labs Backpack' still appears in cart."
        )
        logger.info("PASS — item removed from cart, count and list both updated correctly.")

    # ── Navigation ───────────────────────────────────────────────────────────

    def test_continue_shopping_returns_to_inventory(self):
        """'Continue Shopping' button navigates back to the inventory page."""
        cart_page = self.inventory_page.go_to_cart()
        cart_page.continue_shopping()
        url_confirmed = wait_helper.wait_for_url_contains(self.driver, "inventory.html")
        assert url_confirmed, (
            f"'Continue Shopping' did not navigate to inventory. "
            f"Current URL: {self.driver.current_url}"
        )
        logger.info("PASS — 'Continue Shopping' returns to inventory page.")

    def test_proceed_to_checkout_navigates_to_step_one(self):
        """'Checkout' button navigates to checkout step one."""
        self.inventory_page.add_to_cart_by_index(1)
        cart_page = self.inventory_page.go_to_cart()
        cart_page.proceed_to_checkout()
        url_confirmed = wait_helper.wait_for_url_contains(self.driver, "checkout-step-one")
        assert url_confirmed, (
            f"'Checkout' did not navigate to checkout step one. "
            f"Current URL: {self.driver.current_url}"
        )
        logger.info("PASS — 'Checkout' navigates to checkout step one.")