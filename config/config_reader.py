"""
config_reader.py
Parses config/config.ini and exposes all settings as importable constants.
All other modules import from here — zero hardcoded values anywhere else.
"""

import os
import configparser

# Initialise the parser
config = configparser.ConfigParser()

# Resolve config.ini path relative to this file — works regardless of working directory
current_dir = os.path.dirname(__file__)  # project/config
ini_path = os.path.join(current_dir, 'config.ini')
config.read(ini_path)

# ── Settings ──────────────────────────────────────────────────────────────────
BASE_URL = config.get('settings', 'base_url')
BROWSER  = config.get('settings', 'browser')

# ── Timeouts ──────────────────────────────────────────────────────────────────
TIMEOUT         = config.getint('timeouts', 'timeout')
IMPLICIT_WAIT   = config.getint('timeouts', 'implicit_wait')
EXPLICIT_WAIT   = config.getint('timeouts', 'explicit_wait')
PAGE_LOAD_WAIT  = config.getint('timeouts', 'page_load_wait')

# ── Credentials ───────────────────────────────────────────────────────────────
STANDARD_USER = config.get('credentials', 'standard_user')
LOCKED_USER   = config.get('credentials', 'locked_user')
PROBLEM_USER  = config.get('credentials', 'problem_user')
PASSWORD      = config.get('credentials', 'password')

# ── Paths ─────────────────────────────────────────────────────────────────────
SCREENSHOT_DIR = config.get('paths', 'screenshot_dir')
LOGS_DIR       = config.get('paths', 'log_dir')
REPORTS_DIR    = config.get('paths', 'report_dir')

# ── Logging ───────────────────────────────────────────────────────────────────
LOG_LEVEL       = config.get('logging', 'log_level')
LOG_FORMAT      = config.get('logging', 'log_format',  raw=True)
LOG_DATE_FORMAT = config.get('logging', 'log_datefmt', raw=True)

# ── Test Data ─────────────────────────────────────────────────────────────────
JSON_FILE     = config.get('data', 'json_file')
JSON_FILE_E2E = config.get('data', 'json_file_e2e')