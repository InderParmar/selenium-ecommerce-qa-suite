"""
conftest.py
pytest session configuration — WebDriver lifecycle, cross-browser support,
automatic screenshot capture on test failure, and HTML report customisation.
"""

import os
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from config.config_reader import BASE_URL, BROWSER, PAGE_LOAD_WAIT, SCREENSHOT_DIR
from utils.logger import get_logger

logger = get_logger(__name__)


def pytest_addoption(parser):
    parser.addoption(
        "--browser", action="store", default=BROWSER,
        help="Browser to run tests on: chrome | safari"
    )


@pytest.fixture(scope="session")
def browser(request):
    return request.config.getoption("--browser")


@pytest.fixture(scope="function")
def setup(request, browser):
    """
    Sets up and tears down the WebDriver for each test function.
    Attaches the driver to the test class so pages can access it.
    """
    browser = browser.lower()
    logger.info("Initialising browser: %s", browser)

    if browser == "chrome":
        chrome_options = Options()
        prefs = {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
            "profile.password_manager_leak_detection": False
        }
        chrome_options.add_experimental_option("prefs", prefs)

        # Auto-headless in CI — GitHub Actions sets CI=true automatically
        if os.environ.get("CI"):
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--window-size=1920,1080")
            logger.info("CI environment detected — running Chrome in headless mode")

        driver = webdriver.Chrome(options=chrome_options)
        
    elif browser == "firefox":
        from selenium.webdriver.firefox.options import Options as FirefoxOptions
        firefox_options = FirefoxOptions()
        if os.environ.get("CI"):
            firefox_options.add_argument("--headless")
        driver = webdriver.Firefox(options=firefox_options)

    elif browser == "safari":
        driver = webdriver.Safari()

    else:
        pytest.fail(f"Unsupported browser: '{browser}'. Use 'chrome' or 'safari'.")

    driver.maximize_window()
    logger.info("Navigating to: %s", BASE_URL)
    driver.get(BASE_URL)
    request.cls.driver = driver

    yield

    logger.info("Test complete — quitting browser")
    driver.quit()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item):
    """
    Captures a screenshot on test failure and embeds it in the HTML report.
    """
    pytest_html = item.config.pluginmanager.getplugin("html")
    outcome = yield
    report = outcome.get_result()
    extra = getattr(report, "extra", [])

    if report.when == "call":
        xfail = hasattr(report, "wasxfail")
        test_failed      = report.failed  and not xfail
        test_skipped_xfail = report.skipped and xfail

        if test_failed or test_skipped_xfail:
            safe_name       = report.nodeid.replace("::", "_").replace("/", "_")
            screenshot_name = f"{safe_name}.png"
            screenshot_path = os.path.join(SCREENSHOT_DIR, screenshot_name)

            try:
                item.cls.driver.save_screenshot(screenshot_path)
                logger.info("Screenshot saved: %s", screenshot_path)
                html_img = (
                    f'<div><img src="{screenshot_name}" alt="Failure screenshot" '
                    f'style="width:320px;height:200px;border:1px solid #ccc;" '
                    f'onclick="window.open(this.src)" align="right"/></div>'
                )
                extra.append(pytest_html.extras.html(html_img))
            except Exception as e:
                logger.error("Could not save screenshot: %s", e)

    report.extra = extra


def pytest_html_report_title(report):
    report.title = "Sauce Demo — Automation Test Report"