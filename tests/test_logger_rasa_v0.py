"""
Tests for logger_rasa_v0.py (src/shared/logger_rasa_v0.py)
"""
import logging
import types
import pytest
from unittest.mock import patch, MagicMock
from src.shared.logger_rasa_v0 import TruncatingColoredFormatter, get_logger

def test_truncating_formatter_truncates():
    fmt = TruncatingColoredFormatter(fmt="%(message)s", max_length=10)
    record = logging.LogRecord(
        name="test", level=logging.INFO, pathname=__file__, lineno=1,
        msg="0123456789ABCDEF", args=(), exc_info=None
    )
    result = fmt.format(record)
    assert result.endswith("…")
    assert len(result) <= 10

def test_truncating_formatter_no_truncation():
    fmt = TruncatingColoredFormatter(fmt="%(message)s", max_length=20)
    record = logging.LogRecord(
        name="test", level=logging.INFO, pathname=__file__, lineno=1,
        msg="short msg", args=(), exc_info=None
    )
    result = fmt.format(record)
    assert result == "short msg"

def test_truncating_formatter_no_max_length():
    fmt = TruncatingColoredFormatter(fmt="%(message)s", max_length=None)
    record = logging.LogRecord(
        name="test", level=logging.INFO, pathname=__file__, lineno=1,
        msg="no truncation", args=(), exc_info=None
    )
    result = fmt.format(record)
    assert result == "no truncation"

def test_get_logger_truncates(monkeypatch):
    # Remove handlers to force new formatter
    logger = logging.getLogger("rasa-bot-test")
    logger.handlers.clear()
    monkeypatch.setattr("src.shared.logger_rasa_v0.get_config", lambda: {"LOG_MESSAGE_MAX_LENGTH": 8})
    monkeypatch.setattr("coloredlogs.install", lambda **kwargs: None)
    monkeypatch.setattr("coloredlogs.DEFAULT_LEVEL_STYLES", {})
    monkeypatch.setattr("coloredlogs.DEFAULT_FIELD_STYLES", {})
    log = get_logger("rasa-bot-test")
    assert log.name == "rasa-bot-test"
    assert log.level == logging.DEBUG

def test_get_logger_invalid_max_length(monkeypatch):
    logger = logging.getLogger("rasa-bot-invalid")
    logger.handlers.clear()
    monkeypatch.setattr("src.shared.logger_rasa_v0.get_config", lambda: {"LOG_MESSAGE_MAX_LENGTH": "notanint"})
    monkeypatch.setattr("coloredlogs.install", lambda **kwargs: None)
    monkeypatch.setattr("coloredlogs.DEFAULT_LEVEL_STYLES", {})
    monkeypatch.setattr("coloredlogs.DEFAULT_FIELD_STYLES", {})
    log = get_logger("rasa-bot-invalid")
    assert log.name == "rasa-bot-invalid"
    assert log.level == logging.DEBUG

def test_get_logger_negative_max_length(monkeypatch):
    logger = logging.getLogger("rasa-bot-neg")
    logger.handlers.clear()
    monkeypatch.setattr("src.shared.logger_rasa_v0.get_config", lambda: {"LOG_MESSAGE_MAX_LENGTH": -1})
    monkeypatch.setattr("coloredlogs.install", lambda **kwargs: None)
    monkeypatch.setattr("coloredlogs.DEFAULT_LEVEL_STYLES", {})
    monkeypatch.setattr("coloredlogs.DEFAULT_FIELD_STYLES", {})
    log = get_logger("rasa-bot-neg")
    assert log.name == "rasa-bot-neg"
    assert log.level == logging.DEBUG
