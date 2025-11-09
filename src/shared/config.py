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


def get_config():
    "Load configuration from environment variables"

    config = {
        "TELEGRAM_API_KEY": os.getenv('TELEGRAM_API_KEY'),
        "RASA_API_URL": os.getenv('RASA_API_URL'),
        "SYSTEM_INSTRUCTIONS_PATH": os.getenv('SYSTEM_INSTRUCTIONS_PATH', str(DEFAULT_SYSTEM_INSTRUCTIONS_PATH)),
        "APP_MODE": os.getenv('APP_MODE', 'GOOGLE_GEMINI'),
        "GOOGLE_GEMINI_API_KEY": os.getenv('GOOGLE_GEMINI_API_KEY'),
    }
    logger.debug(
        "Config cargada | TELEGRAM_KEY=%s | RASA_API_URL=%s | APP_MODE=%s | SYSTEM_PATH=%s | GEMINI_KEY=%s",
        bool(config["TELEGRAM_API_KEY"]),
        config["RASA_API_URL"],
        config["APP_MODE"],
        config["SYSTEM_INSTRUCTIONS_PATH"],
        bool(config["GOOGLE_GEMINI_API_KEY"]),
    )
    return config
