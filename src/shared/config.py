"""Configuration helpers."""

import os
from pathlib import Path
from dotenv import load_dotenv
import logging

DEFAULT_SYSTEM_INSTRUCTIONS_PATH = (
    Path(__file__).resolve().parent.parent
    / "infrastructure"
    / "google_generative_ai"
    / "system_instructions.json"
)

load_dotenv()

logger = logging.getLogger("config")


def _parse_bool(val, default=False):
    if val is None:
        return default
    if isinstance(val, bool):
        return val
    return str(val).strip().lower() in ("1", "true", "yes", "on")


def get_config():
    """
    Load and validate configuration from environment variables.
    Raises ValueError if a required variable is missing or invalid.
    """
    config = {}

    # TELEGRAM_API_KEY (obligatorio)
    telegram_key = os.getenv("TELEGRAM_API_KEY")
    if (
        not telegram_key
        or not isinstance(telegram_key, str)
        or len(telegram_key.strip()) < 10
    ):
        logger.error("TELEGRAM_API_KEY es obligatorio y debe ser un string válido.")
        raise ValueError("TELEGRAM_API_KEY es obligatorio y debe ser un string válido.")
    config["TELEGRAM_API_KEY"] = telegram_key.strip()

    # GOOGLE_GEMINI_API_KEY (obligatorio)
    gemini_key = os.getenv("GOOGLE_GEMINI_API_KEY")
    if (
        not gemini_key
        or not isinstance(gemini_key, str)
        or len(gemini_key.strip()) < 10
    ):
        logger.error(
            "GOOGLE_GEMINI_API_KEY es obligatorio y debe ser un string válido."
        )
        raise ValueError(
            "GOOGLE_GEMINI_API_KEY es obligatorio y debe ser un string válido."
        )
    config["GOOGLE_GEMINI_API_KEY"] = gemini_key.strip()

    # RASA_REST_URL (opcional)
    rasa_url = os.getenv("RASA_REST_URL", "http://localhost:5005/webhooks/rest/webhook")
    if not isinstance(rasa_url, str) or not rasa_url.startswith("http"):
        logger.warning("RASA_REST_URL inválido, usando valor por defecto.")
        rasa_url = "http://localhost:5005/webhooks/rest/webhook"
    config["RASA_REST_URL"] = rasa_url

    # DISABLE_RASA (opcional)
    disable_rasa = _parse_bool(os.getenv("DISABLE_RASA"), default=False)
    config["DISABLE_RASA"] = disable_rasa

    # LOG_MESSAGE_MAX_LENGTH (opcional)
    raw_max_length = os.getenv("LOG_MESSAGE_MAX_LENGTH", "160")
    try:
        max_length = int(raw_max_length)
        if max_length <= 0:
            raise ValueError
    except Exception:
        logger.warning("LOG_MESSAGE_MAX_LENGTH inválido, usando 160.")
        max_length = 160
    config["LOG_MESSAGE_MAX_LENGTH"] = max_length

    logger.debug(
        "Config cargada | TELEGRAM_KEY=%s | GEMINI_KEY=%s | RASA_URL=%s | DISABLE_RASA=%s | LOG_MESSAGE_MAX_LENGTH=%s",
        bool(config["TELEGRAM_API_KEY"]),
        bool(config["GOOGLE_GEMINI_API_KEY"]),
        config["RASA_REST_URL"],
        config["DISABLE_RASA"],
        config["LOG_MESSAGE_MAX_LENGTH"],
    )
    return config


__all__ = ["get_config", "DEFAULT_SYSTEM_INSTRUCTIONS_PATH"]
