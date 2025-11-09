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
        "GOOGLE_GEMINI_API_KEY": os.getenv('GOOGLE_GEMINI_API_KEY'),
    }
    logger.debug(
        "Config cargada | TELEGRAM_KEY=%s | GEMINI_KEY=%s",
        bool(config["TELEGRAM_API_KEY"]),
        bool(config["GOOGLE_GEMINI_API_KEY"]),
    )
    return config


__all__ = ["get_config", "DEFAULT_SYSTEM_INSTRUCTIONS_PATH"]
