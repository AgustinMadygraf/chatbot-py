import os
import pytest
from src.shared.config import get_config


def set_env_vars(env_dict):
    for k, v in env_dict.items():
        os.environ[k] = v

def clear_env_vars(keys):
    for k in keys:
        if k in os.environ:
            del os.environ[k]

def test_valid_config(monkeypatch):
    monkeypatch.setenv("TELEGRAM_API_KEY", "1234567890abcdef")
    monkeypatch.setenv("GOOGLE_GEMINI_API_KEY", "abcdef1234567890")
    monkeypatch.setenv("RASA_REST_URL", "http://localhost:1234/webhook")
    monkeypatch.setenv("DISABLE_RASA", "true")
    monkeypatch.setenv("LOG_MESSAGE_MAX_LENGTH", "200")
    config = get_config()
    assert config["TELEGRAM_API_KEY"] == "1234567890abcdef"
    assert config["GOOGLE_GEMINI_API_KEY"] == "abcdef1234567890"
    assert config["RASA_REST_URL"] == "http://localhost:1234/webhook"
    assert config["DISABLE_RASA"] is True
    assert config["LOG_MESSAGE_MAX_LENGTH"] == 200

def test_missing_telegram_key(monkeypatch):
    monkeypatch.delenv("TELEGRAM_API_KEY", raising=False)
    monkeypatch.setenv("GOOGLE_GEMINI_API_KEY", "abcdef1234567890")
    with pytest.raises(ValueError):
        get_config()

def test_missing_gemini_key(monkeypatch):
    monkeypatch.setenv("TELEGRAM_API_KEY", "1234567890abcdef")
    monkeypatch.delenv("GOOGLE_GEMINI_API_KEY", raising=False)
    with pytest.raises(ValueError):
        get_config()

def test_invalid_telegram_key(monkeypatch):
    monkeypatch.setenv("TELEGRAM_API_KEY", "short")
    monkeypatch.setenv("GOOGLE_GEMINI_API_KEY", "abcdef1234567890")
    with pytest.raises(ValueError):
        get_config()

def test_invalid_gemini_key(monkeypatch):
    monkeypatch.setenv("TELEGRAM_API_KEY", "1234567890abcdef")
    monkeypatch.setenv("GOOGLE_GEMINI_API_KEY", "short")
    with pytest.raises(ValueError):
        get_config()

def test_invalid_rasa_url(monkeypatch):
    monkeypatch.setenv("TELEGRAM_API_KEY", "1234567890abcdef")
    monkeypatch.setenv("GOOGLE_GEMINI_API_KEY", "abcdef1234567890")
    monkeypatch.setenv("RASA_REST_URL", "not_a_url")
    config = get_config()
    assert config["RASA_REST_URL"] == "http://localhost:5005/webhooks/rest/webhook"

def test_invalid_disable_rasa(monkeypatch):
    monkeypatch.setenv("TELEGRAM_API_KEY", "1234567890abcdef")
    monkeypatch.setenv("GOOGLE_GEMINI_API_KEY", "abcdef1234567890")
    monkeypatch.setenv("DISABLE_RASA", "notabool")
    config = get_config()
    assert config["DISABLE_RASA"] is False

def test_invalid_log_message_max_length(monkeypatch):
    monkeypatch.setenv("TELEGRAM_API_KEY", "1234567890abcdef")
    monkeypatch.setenv("GOOGLE_GEMINI_API_KEY", "abcdef1234567890")
    monkeypatch.setenv("LOG_MESSAGE_MAX_LENGTH", "notanint")
    config = get_config()
    assert config["LOG_MESSAGE_MAX_LENGTH"] == 160
    monkeypatch.setenv("LOG_MESSAGE_MAX_LENGTH", "-5")
    config = get_config()
    assert config["LOG_MESSAGE_MAX_LENGTH"] == 160
