"""
test_e2e.py
-----------
End-to-end test suite — validates the full purchase flow from
login through order confirmation as a single integrated scenario.
Includes a data-driven variant covering both success and error paths.
"""
import pytest
from config.config_reader import STANDARD_USER, PASSWORD, JSON_FILE_E2E
from utils import wait_helper
from utils import data_reader
from pages.login_page import Login_page
from pages.inventory_page import Inventory_page
from pages.cart_page import Cart_page
from pages.checkout_page import Checkout_page
from utils.logger import get_logger

logger = get_logger(__name__)


@pytest.mark.usefixtures("setup")
class TestE2E:
    """End-to-end test suite covering the full purchase lifecycle."""

    @pytest.fixture(autouse=True)
    def initialise_pages(self, setup):
        """Log in as standard_user and initialise all page objects."""
        self.login_page = Login_page(self.driver)
        self.inventory_page = Inventory_page(self.driver)
        self.cart_page = Cart_page(self.driver)
        self.checkout_page = Checkout_page(self.driver)
        self.login_page.login(STANDARD_USER, PASSWORD)

    def test_full_purchase_flow_standard_user(self):
        """Full happy-path purchase: add items → cart → checkout → confirm order.

        Validates:
          - Cart item count after adding two items
          - Final total equals item subtotal + tax (float tolerance 0.01)
          - Order confirmation screen is displayed after finishing
        """
        self.inventory_page.add_to_cart_by_name("Sauce Labs Backpack")
        self.inventory_page.add_to_cart_by_name("Sauce Labs Fleece Jacket")

        cart_page = self.inventory_page.go_to_cart()
        assert cart_page.get_item_count() == 2, (
            f"Expected 2 items in cart before checkout, "
            f"found {cart_page.get_item_count()}."
        )

        cart_page.proceed_to_checkout()
        self.checkout_page.fill_checkout_info("John", "Doe", "M5V2T6")
        self.checkout_page.click_continue()

        item_total = self.checkout_page.get_item_total()
        tax = self.checkout_page.get_tax()
        total = self.checkout_page.get_total()
        assert abs(total - (item_total + tax)) < 0.01, (
            f"Total mismatch: item_total({item_total}) + tax({tax}) "
            f"≠ displayed total({total})."
        )

        self.checkout_page.click_finish()
        assert self.checkout_page.is_order_confirmed(), (
            "Order confirmation screen not displayed after completing checkout."
        )
        logger.info("PASS — full E2E purchase flow completed successfully.")

    @pytest.mark.parametrize(
        "first_name, last_name, postal_code, expected",
        data_reader.read_data_from_json(JSON_FILE_E2E)
    )
    def test_full_purchase_flow_data_driven(
        self, first_name, last_name, postal_code, expected
    ):
        """Data-driven E2E test — exercises both success and validation-error paths.

        JSON rows with expected='success' assert full order completion.
        JSON rows with expected='zip_error' assert the postal code error message.
        """
        self.inventory_page.add_to_cart_by_name("Sauce Labs Backpack")
        self.inventory_page.add_to_cart_by_name("Sauce Labs Fleece Jacket")

        cart_page = self.inventory_page.go_to_cart()
        assert cart_page.get_item_count() == 2, (
            f"Expected 2 items in cart, found {cart_page.get_item_count()}."
        )

        cart_page.proceed_to_checkout()
        self.checkout_page.fill_checkout_info(first_name, last_name, postal_code)
        self.checkout_page.click_continue()

        if expected == "success":
            item_total = self.checkout_page.get_item_total()
            tax = self.checkout_page.get_tax()
            total = self.checkout_page.get_total()
            assert abs(total - (item_total + tax)) < 0.01, (
                f"Total mismatch on success path: "
                f"{item_total} + {tax} ≠ {total}."
            )
            self.checkout_page.click_finish()
            assert self.checkout_page.is_order_confirmed(), (
                "Order confirmation not shown on success path."
            )
            logger.info(
                "PASS — data-driven E2E success path completed for '%s %s'.",
                first_name, last_name
            )

        elif expected == "zip_error":
            error_message = self.checkout_page.get_error_message()
            assert "Postal Code is required" in error_message, (
                f"Expected postal code error on zip_error path, "
                f"got: '{error_message}'"
            )
            logger.info(
                "PASS — data-driven E2E zip_error path correctly blocked for '%s %s'.",
                first_name, last_name
            )

        else:
            pytest.fail(
                f"Unrecognised 'expected' value in JSON: '{expected}'. "
                f"Use 'success' or 'zip_error'."
            )