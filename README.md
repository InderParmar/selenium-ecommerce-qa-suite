# selenium-ecommerce-qa-suite

[![selenium-ecommerce-qa-suite](https://github.com/InderParmar/selenium-ecommerce-qa-suite/actions/workflows/test_pipeline.yml/badge.svg)](https://github.com/InderParmar/selenium-ecommerce-qa-suite/actions/workflows/test_pipeline.yml)
![Python](https://img.shields.io/badge/python-3.11-blue?logo=python&logoColor=white)
![Selenium](https://img.shields.io/badge/selenium-4.x-green?logo=selenium&logoColor=white)
![pytest](https://img.shields.io/badge/tested%20with-pytest-orange)
![Cross-Browser](https://img.shields.io/badge/browsers-Chrome%20%7C%20Firefox-informational)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

> A production-grade Selenium WebDriver automation framework built in Python —
> validating an e-commerce application across **36 test cases**, **5 modules**,
> and **2 browsers**, with full CI/CD integration via GitHub Actions.

---

## Demo

![ShopSafe Test Suite Running](docs/demo.gif)

> *36 tests · Chrome + Firefox · auto-generated HTML report with failure screenshots*

---

## What this project covers

| Module | Test Cases | Coverage |
|---|---|---|
| Login | 9 | Valid login, locked-out user, wrong password, empty fields, error dismissal, data-driven via JSON |
| Inventory | 9 | Page state, all 4 sort orders with list-comparison assertions, cart badge management |
| Cart | 6 | Item display, count validation, price consistency between inventory and cart, remove item, navigation |
| Checkout | 9 | Step 1 form validation, step 2 float math assertions (subtotal + tax = total), order confirmation |
| End-to-End | 2 | Full purchase flow, data-driven checkout with success and error paths |
| **Total** | **36** | |

---

## Framework architecture

```
selenium-ecommerce-qa-suite/
│
├── pages/                        # Page Object Model layer — all Selenium logic lives here
│   ├── base_page.py              # Shared methods: click, enter text, get text, scoped search
│   ├── login_page.py             # Login flow, error handling, dismiss error
│   ├── inventory_page.py         # Sort validation, cart management, page chaining
│   ├── cart_page.py              # Item validation, price check, checkout navigation
│   └── checkout_page.py         # Form validation, float math assertions, order confirmation
│
├── tests/                        # Test layer — zero Selenium, only assertions
│   ├── conftest.py               # Driver fixture, cross-browser, headless CI, screenshot on failure
│   ├── test_login.py
│   ├── test_inventory.py
│   ├── test_cart.py
│   ├── test_checkout.py
│   └── test_e2e.py
│
├── utils/
│   ├── wait_helper.py            # All WebDriverWait calls centralised here
│   ├── logger.py                 # Console + file logging with daily log rotation
│   ├── config_reader.py          # Reads config.ini — zero hardcoded values
│   └── data_reader.py            # JSON data loader for parametrized tests
│
├── test_data/                    # External JSON test data — decoupled from test logic
│   ├── login_data.json
│   ├── checkout_data.json
│   └── e2e_data.json
│
├── config/
│   └── config.ini                # Browser, base URL, timeouts, credentials, paths
│
├── reports/                      # Auto-generated — gitignored except .gitkeep
│   ├── screenshots/              # Failure screenshots named by test ID + timestamp
│   └── logs/                     # Daily rotating log files
│
└── .github/workflows/
    └── test_pipeline.yml         # GitHub Actions CI — parallel Chrome + Firefox matrix
```

---

## Key technical decisions

**Explicit waits only — never `time.sleep()`.**
All `WebDriverWait` calls are centralised in `wait_helper.py`. Tests and page objects never import `WebDriverWait` directly. If the wait strategy changes, one file changes.

**Zero Selenium in the test layer.**
Test files contain no `By`, `WebDriverWait`, or `driver` references. Tests call page object methods and make assertions — nothing else. This is what makes the framework maintainable at scale.

**Logic-based assertions over click-based assertions.**
Sorting is validated by extracting all product names into a Python list and asserting `names == sorted(names)` — not by checking individual hardcoded product names. Checkout math uses `abs(total - (item_total + tax)) < 0.01` to handle float precision correctly.

**Scoped DOM traversal for price consistency.**
`get_price_by_name()` uses a `parent` parameter to scope `WebDriverWait` to a specific cart item container — guaranteeing name and price belong to the same product regardless of DOM rendering order.

**Page chaining pattern.**
`inventory.go_to_cart()` returns a `CartPage` instance. `cart.proceed_to_checkout()` returns a `CheckoutPage` instance. Tests read as user stories, not automation scripts.

**Auto-headless in CI.**
`conftest.py` detects `os.environ.get("CI")` and activates headless mode automatically. Local runs stay headed for debugging. No manual flag switching required.

---

## Highlighted assertions

**Sort validation — one line validates the entire sorted state:**
```python
names = inventory_page.get_all_product_names()
assert names == sorted(names)
# Works for 6 products or 600. No hardcoded names. Never needs updating.
```

**Price sort validation with float conversion:**
```python
prices = [float(p.strip("$")) for p in inventory_page.get_all_product_prices()]
assert prices == sorted(prices)
```

**Checkout math with float tolerance:**
```python
item_total = checkout_page.get_item_total()   # returns float, e.g. 39.98
tax        = checkout_page.get_tax()           # returns float, e.g. 3.20
total      = checkout_page.get_total()         # returns float, e.g. 43.18
assert abs(total - (item_total + tax)) < 0.01
# Uses tolerance instead of == to handle floating point precision correctly
```

**Price consistency between inventory and cart:**
```python
# Verified using parent-scoped DOM search — not index matching across two lists
cart_price = cart_page.get_price_by_name("Sauce Labs Backpack")
assert inventory_price == cart_price
```

---

## CI/CD pipeline

Every push to `main` triggers the full test suite on Chrome and Firefox in parallel.

```
push to main
    │
    ├── job: test (chrome)          ├── job: test (firefox)
    │   ├── checkout code           │   ├── checkout code
    │   ├── setup Python 3.11       │   ├── setup Python 3.11
    │   ├── install dependencies    │   ├── install dependencies
    │   ├── setup Chrome            │   ├── setup Firefox
    │   ├── run pytest              │   ├── run pytest
    │   ├── upload HTML report      │   ├── upload HTML report
    │   └── upload screenshots      │   └── upload screenshots
```

- HTML reports upload as downloadable artifacts after every run
- Failure screenshots are captured automatically via `pytest_runtest_makereport` hook
- `fail-fast: false` ensures both browsers always complete even if one fails
- Artifacts retained for 30 days per run

---

## Quick start

```bash
# Clone the repo
git clone https://github.com/InderParmar/selenium-ecommerce-qa-suite.git
cd selenium-ecommerce-qa-suite

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt

# Run the full test suite (Chrome, headed)
pytest tests/

# Run on Firefox
pytest tests/ --browser=firefox

# Run with HTML report
pytest tests/ --html=reports/report.html --self-contained-html

# Run smoke tests only
pytest tests/ -m smoke
```

---

## Test data

Test data is fully externalised — no hardcoded values inside test files.

**`login_data.json`** — parametrizes `test_data_driven_valid_login`:
```json
[
  { "username": "standard_user",  "password": "secret_sauce" }
]
```

**`e2e_data.json`** — parametrizes `test_full_purchase_flow_data_driven`:
```json
[
  { "first_name": "John",  "last_name": "Doe",   "postal_code": "M5V2T6", "expected": "success"   },
  { "first_name": "Jane",  "last_name": "Smith",  "postal_code": "",       "expected": "zip_error" }
]
```

---

## Reporting and debugging

After a test run, three layers of output are available:

**HTML report** — `reports/report_<browser>.html`
Full test results with pass/fail status, duration, and embedded failure screenshots. Self-contained single file — email it, share it, open it anywhere.

**Failure screenshots** — `reports/screenshots/`
Auto-captured at the exact moment of failure via `pytest_runtest_makereport` hook. Named by test node ID for instant identification.

**Log files** — `reports/logs/test_run_YYYYMMDD.log`
Structured `INFO / WARNING / ERROR` output with timestamps, module names, and action context. New file per day — no unbounded log growth.

---

## Tech stack

| Tool | Version | Purpose |
|---|---|---|
| Python | 3.11 | Core language |
| Selenium WebDriver | 4.x | Browser automation |
| pytest | 9.x | Test runner and fixtures |
| pytest-html | 4.x | HTML report generation |
| webdriver-manager | latest | Automatic driver management |
| softest | latest | Soft assertions for multi-element validation |
| GitHub Actions | — | CI/CD pipeline |

---

## Project status

- [x] Phase 1 — Framework structure
- [x] Phase 2 — Core framework skeleton (BasePage, wait_helper, logger, config)
- [x] Phase 3 — Page Object Model layer (4 page classes)
- [x] Phase 4 — Full test suite (36 test cases)
- [x] Phase 5 — CI/CD integration (Chrome + Firefox parallel matrix)

---

## Author

**Inderpreet Singh Parmar**
QA Automation Engineer · Toronto, ON
[LinkedIn](https://ca.linkedin.com/in/inderpreet-singh-parmar-7abb23230) · [Portfolio](https://inder-website.vercel.app) · [GitHub](https://github.com/InderParmar)