"""
logger.py
Factory function that returns a named logger with both a console handler
and a daily rotating file handler. Call get_logger(__name__) in every module.
"""

import logging
from datetime import datetime
import os
from config.config_reader import LOGS_DIR, LOG_LEVEL, LOG_FORMAT, LOG_DATE_FORMAT


def get_logger(caller_name: str, loglevel: str = LOG_LEVEL) -> logging.Logger:
    logger = logging.getLogger(caller_name)

    # Prevent duplicate handlers if get_logger is called multiple times for the same name
    if logger.handlers:
        return logger

    logger.setLevel(loglevel)

    # ── Console handler ───────────────────────────────────────────────────────
    console_handler = logging.StreamHandler()
    console_handler.setLevel(loglevel)
    console_handler.setFormatter(
        logging.Formatter(fmt=LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
    )

    # ── File handler — daily log file ─────────────────────────────────────────
    log_filename = datetime.now().strftime("test_run_%Y%m%d.log")
    log_filepath = os.path.join(LOGS_DIR, log_filename)
    file_handler = logging.FileHandler(log_filepath, "a", encoding="utf-8")
    file_handler.setLevel(loglevel)
    file_handler.setFormatter(
        logging.Formatter(fmt=LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
    )

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger