"""
test_checkout.py
----------------
Test suite for the Checkout module — covers form field validation
(step 1), math assertions for item total, tax, and final total
(step 2), order completion, and post-order navigation.
"""
import pytest
from config.config_reader import STANDARD_USER, PASSWORD
from utils import wait_helper
from pages.login_page import Login_page
from pages.inventory_page import Inventory_page
from pages.cart_page import Cart_page
from pages.checkout_page import Checkout_page
from utils.logger import get_logger

logger = get_logger(__name__)

CHECKOUT_ITEMS = ["Sauce Labs Backpack", "Sauce Labs Bike Light"]
VALID_FIRST = "John"
VALID_LAST = "Doe"
VALID_ZIP = "M5V2T6"


@pytest.mark.usefixtures("setup")
class TestCheckout:
    """Checkout page test suite — step 1 validation and step 2 math assertions."""

    @pytest.fixture(autouse=True)
    def initialise_pages(self, setup):
        """Log in as standard_user before each test.
        Items are added to cart inside individual tests — cart state is not shared."""
        self.login_page = Login_page(self.driver)
        self.inventory_page = Inventory_page(self.driver)
        self.cart_page = Cart_page(self.driver)
        self.checkout_page = Checkout_page(self.driver)
        self.login_page.login(STANDARD_USER, PASSWORD)

    # ── Step 1 — form validation ─────────────────────────────────────────────

    def test_valid_checkout_info_proceeds_to_step_two(self):
        """Completing step 1 with valid data navigates to checkout step 2."""
        self._add_items_and_reach_checkout()
        self.checkout_page.fill_checkout_info(VALID_FIRST, VALID_LAST, VALID_ZIP)
        self.checkout_page.click_continue()
        url_confirmed = wait_helper.wait_for_url_contains(self.driver, "checkout-step-two")
        assert url_confirmed, (
            f"Valid checkout info did not proceed to step 2. "
            f"Current URL: {self.driver.current_url}"
        )
        logger.info("PASS — valid checkout info proceeds to step 2.")

    def test_missing_first_name_shows_error(self):
        """Omitting first name shows 'First Name is required' error on step 1."""
        self._add_items_and_reach_checkout()
        self.checkout_page.enter_last_name(VALID_LAST)
        self.checkout_page.enter_postal_code(VALID_ZIP)
        self.checkout_page.click_continue()
        error_message = self.checkout_page.get_error_message()
        assert "First Name is required" in error_message, (
            f"Expected 'First Name is required', got: '{error_message}'"
        )
        logger.info("PASS — missing first name shows correct validation error.")

    def test_missing_last_name_shows_error(self):
        """Omitting last name shows 'Last Name is required' error on step 1."""
        self._add_items_and_reach_checkout()
        self.checkout_page.enter_first_name(VALID_FIRST)
        self.checkout_page.enter_postal_code(VALID_ZIP)
        self.checkout_page.click_continue()
        error_message = self.checkout_page.get_error_message()
        assert "Last Name is required" in error_message, (
            f"Expected 'Last Name is required', got: '{error_message}'"
        )
        logger.info("PASS — missing last name shows correct validation error.")

    def test_missing_postal_code_shows_error(self):
        """Omitting postal code shows 'Postal Code is required' error on step 1."""
        self._add_items_and_reach_checkout()
        self.checkout_page.enter_first_name(VALID_FIRST)
        self.checkout_page.enter_last_name(VALID_LAST)
        self.checkout_page.click_continue()
        error_message = self.checkout_page.get_error_message()
        assert "Postal Code is required" in error_message, (
            f"Expected 'Postal Code is required', got: '{error_message}'"
        )
        logger.info("PASS — missing postal code shows correct validation error.")

    # ── Step 2 — math assertions ─────────────────────────────────────────────

    def test_item_total_matches_sum_of_cart_prices(self):
        """Item subtotal on checkout step 2 matches the sum of cart item prices."""
        self.inventory_page.add_to_cart_by_name(CHECKOUT_ITEMS[0])
        self.inventory_page.add_to_cart_by_name(CHECKOUT_ITEMS[1])
        cart_page = self.inventory_page.go_to_cart()
        cart_prices = self._get_cart_prices_as_floats()
        expected_subtotal = sum(cart_prices)
        cart_page.proceed_to_checkout()
        self.checkout_page.fill_checkout_info(VALID_FIRST, VALID_LAST, VALID_ZIP)
        self.checkout_page.click_continue()
        checkout_item_total = self.checkout_page.get_item_total()
        assert abs(expected_subtotal - checkout_item_total) < 0.01, (
            f"Item subtotal mismatch. Cart sum: {expected_subtotal}, "
            f"Checkout shows: {checkout_item_total}"
        )
        logger.info(
            "PASS — checkout item total %.2f matches cart price sum %.2f.",
            checkout_item_total, expected_subtotal
        )

    def test_tax_amount_is_positive(self):
        """Tax value on checkout step 2 is a positive number."""
        self._add_items_proceed_to_step_two()
        tax = self.checkout_page.get_tax()
        assert tax > 0, f"Tax should be positive, got {tax}."
        logger.info("PASS — tax is positive: %.2f", tax)

    def test_final_total_equals_item_total_plus_tax(self):
        """Total on checkout step 2 equals item subtotal + tax (float tolerance 0.01)."""
        self._add_items_proceed_to_step_two()
        item_total = self.checkout_page.get_item_total()
        tax = self.checkout_page.get_tax()
        total = self.checkout_page.get_total()
        assert abs(total - (item_total + tax)) < 0.01, (
            f"Total mismatch: item_total({item_total}) + tax({tax}) "
            f"= {item_total + tax}, but displayed total is {total}."
        )
        logger.info(
            "PASS — total %.2f equals item_total %.2f + tax %.2f.",
            total, item_total, tax
        )

    # ── Order completion ─────────────────────────────────────────────────────

    def test_order_completes_and_shows_confirmation(self):
        """Completing the full checkout flow shows the order confirmation message."""
        self._add_items_proceed_to_step_two()
        self.checkout_page.click_finish()
        assert self.checkout_page.is_order_confirmed(), (
            "Order confirmation screen not displayed after clicking Finish."
        )
        confirmation_message = self.checkout_page.get_confirmation_message()
        assert "Thank you for your order" in confirmation_message, (
            f"Unexpected confirmation message: '{confirmation_message}'"
        )
        logger.info("PASS — order completed, confirmation message displayed.")

    def test_back_home_after_order_returns_to_inventory(self):
        """'Back Home' button after order confirmation navigates to inventory."""
        self.inventory_page.add_to_cart_by_index(3)
        self.inventory_page.add_to_cart_by_index(4)
        cart_page = self.inventory_page.go_to_cart()
        cart_page.proceed_to_checkout()
        self.checkout_page.fill_checkout_info(VALID_FIRST, VALID_LAST, VALID_ZIP)
        self.checkout_page.click_continue()
        self.checkout_page.click_finish()
        assert self.checkout_page.is_order_confirmed(), (
            "Precondition failed — order confirmation not shown."
        )
        self.checkout_page.click_back_home()
        url_confirmed = wait_helper.wait_for_url_contains(self.driver, "inventory.html")
        assert url_confirmed, (
            f"'Back Home' did not navigate to inventory. "
            f"Current URL: {self.driver.current_url}"
        )
        logger.info("PASS — 'Back Home' returns to inventory after order completion.")

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _add_items_and_reach_checkout(self):
        """Add one item and navigate to checkout step 1."""
        self.inventory_page.add_to_cart_by_index(1)
        cart_page = self.inventory_page.go_to_cart()
        cart_page.proceed_to_checkout()

    def _add_items_proceed_to_step_two(self):
        """Add two items, navigate through checkout step 1 to reach step 2."""
        self.inventory_page.add_to_cart_by_name(CHECKOUT_ITEMS[0])
        self.inventory_page.add_to_cart_by_name(CHECKOUT_ITEMS[1])
        cart_page = self.inventory_page.go_to_cart()
        cart_page.proceed_to_checkout()
        self.checkout_page.fill_checkout_info(VALID_FIRST, VALID_LAST, VALID_ZIP)
        self.checkout_page.click_continue()

    def _get_cart_prices_as_floats(self):
        """Get current cart item prices stripped of $ prefix as float list."""
        prices = self.cart_page.get_item_prices()
        return [float(price.strip("$")) for price in prices]