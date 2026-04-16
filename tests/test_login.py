"""
test_login.py
-------------
Test suite for the Login module — covers valid login flows,
negative scenarios, field validation, error dismissal,
and data-driven login via JSON parametrize.
"""
import pytest
from config.config_reader import STANDARD_USER, LOCKED_USER, PROBLEM_USER, PASSWORD, JSON_FILE
from utils import wait_helper
from utils import data_reader
from pages.login_page import Login_page
from utils.logger import get_logger

logger = get_logger(__name__)


@pytest.mark.usefixtures("setup")
class TestLogin:
    """Login page test suite."""

    @pytest.fixture(autouse=True)
    def initialise_pages(self, setup):
        """Initialise LoginPage before each test. Does NOT call login() —
        these tests are validating the login feature itself."""
        self.login_page = Login_page(self.driver)

    # ── Positive scenarios ───────────────────────────────────────────────────

    def test_valid_login_standard_user(self):
        """Standard user logs in successfully and lands on inventory page."""
        self.login_page.login(STANDARD_USER, PASSWORD)
        url_confirmed = wait_helper.wait_for_url_contains(self.driver, "inventory.html")
        assert url_confirmed, (
            f"Login failed — URL did not contain 'inventory.html'. "
            f"Current URL: {self.driver.current_url}"
        )
        logger.info("PASS — standard_user redirected to inventory page.")

    def test_valid_login_problem_user(self):
        """Problem user logs in successfully and lands on inventory page."""
        self.login_page.login(PROBLEM_USER, PASSWORD)
        url_confirmed = wait_helper.wait_for_url_contains(self.driver, "inventory.html")
        assert url_confirmed, (
            f"Login failed — URL did not contain 'inventory.html'. "
            f"Current URL: {self.driver.current_url}"
        )
        logger.info("PASS — problem_user redirected to inventory page.")

    # ── Negative scenarios ───────────────────────────────────────────────────

    def test_locked_out_user_shows_error(self):
        """Locked-out user sees the correct error banner — cannot log in."""
        self.login_page.login(LOCKED_USER, PASSWORD)
        assert self.login_page.is_error_displayed(), (
            f"No error banner displayed for locked_out_user ({LOCKED_USER})."
        )
        assert "Sorry, this user has been locked out." in self.login_page.get_error_message(), (
            f"Unexpected error message: '{self.login_page.get_error_message()}'"
        )
        logger.info("PASS — locked_out_user correctly blocked with error message.")

    def test_wrong_password_shows_error(self):
        """Wrong password displays an error and does not navigate to inventory."""
        self.login_page.login(STANDARD_USER, "INVALID_PASSWORD")
        assert self.login_page.is_error_displayed(), (
            f"No error banner displayed for wrong password attempt."
        )
        current_url = self.driver.current_url
        assert "inventory.html" not in current_url, (
            f"User was incorrectly redirected to inventory with wrong password. "
            f"Current URL: {current_url}"
        )
        logger.info("PASS — wrong password correctly blocked with error message.")

    # ── Field validation ─────────────────────────────────────────────────────

    def test_empty_username_shows_error(self):
        """Submitting with no username shows 'Username is required' error."""
        self.login_page.enter_password(PASSWORD)
        self.login_page.click_login()
        assert self.login_page.is_error_displayed(), "No error banner for empty username."
        assert "Username is required" in self.login_page.get_error_message(), (
            f"Unexpected error message: '{self.login_page.get_error_message()}'"
        )
        logger.info("PASS — empty username correctly shows validation error.")

    def test_empty_password_shows_error(self):
        """Submitting with no password shows 'Password is required' error."""
        self.login_page.enter_username(STANDARD_USER)
        self.login_page.click_login()
        assert self.login_page.is_error_displayed(), "No error banner for empty password."
        assert "Password is required" in self.login_page.get_error_message(), (
            f"Unexpected error message: '{self.login_page.get_error_message()}'"
        )
        logger.info("PASS — empty password correctly shows validation error.")

    def test_both_fields_empty_shows_error(self):
        """Submitting with both fields empty shows 'Username is required' error."""
        self.login_page.click_login()
        assert self.login_page.is_error_displayed(), "No error banner for both fields empty."
        assert "Username is required" in self.login_page.get_error_message(), (
            f"Unexpected error message: '{self.login_page.get_error_message()}'"
        )
        logger.info("PASS — both fields empty correctly shows validation error.")

    # ── Error dismissal ──────────────────────────────────────────────────────

    def test_error_banner_dismissal(self):
        """Error banner closes when the dismiss (X) button is clicked."""
        self.login_page.login(LOCKED_USER, PASSWORD)
        assert self.login_page.is_error_displayed(), "Precondition failed — no error to dismiss."
        self.login_page.dismiss_error()
        assert not self.login_page.is_error_displayed(), (
            "Error banner is still visible after clicking dismiss."
        )
        logger.info("PASS — error banner dismissed successfully.")

    # ── Data-driven ──────────────────────────────────────────────────────────

    @pytest.mark.parametrize("username, password", data_reader.read_data_from_json(JSON_FILE))
    def test_data_driven_valid_login(self, username, password):
        """Data-driven test — each JSON row represents a valid user credential set."""
        self.login_page.login(username, password)
        url_confirmed = wait_helper.wait_for_url_contains(self.driver, "inventory.html")
        assert url_confirmed, (
            f"Data-driven login failed for user '{username}'. "
            f"Current URL: {self.driver.current_url}"
        )
        logger.info("PASS — data-driven login succeeded for user: %s", username)