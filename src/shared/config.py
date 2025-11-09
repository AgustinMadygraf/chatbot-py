"""Configuration helpers."""

import os
from pathlib import Path
from dotenv import load_dotenv

DEFAULT_SYSTEM_INSTRUCTIONS_PATH = (
    Path(__file__).resolve().parent.parent
    / "infrastructure"
    / "google_generative_ai"
    / "system_instructions.json.example"
)

load_dotenv()


def get_config():
    "Load configuration from environment variables"

    config = {
        "ACCOUNT_SID": os.getenv('TWILIO_ACCOUNT_SID'),
        "AUTH_TOKEN": os.getenv('TWILIO_AUTH_TOKEN'),
        "LOG_LEVEL": os.getenv('LOG_LEVEL', 'DEBUG'),
        "TELEGRAM_API_KEY": os.getenv('TELEGRAM_API_KEY'),
        "TELEGRAM_MODE": os.getenv('TELEGRAM_MODE', 'polling'),
        "RASA_API_URL": os.getenv('RASA_API_URL', 'http://localhost:5005/webhooks/rest/webhook'),
        "SYSTEM_INSTRUCTIONS_PATH": os.getenv('SYSTEM_INSTRUCTIONS_PATH', str(DEFAULT_SYSTEM_INSTRUCTIONS_PATH)),
        "NGROK_DOMAIN": os.getenv('NGROK_DOMAIN'),
        "APP_MODE": os.getenv('APP_MODE', 'GOOGLE_GEMINI'),
    }

    if not config["ACCOUNT_SID"] or not config["AUTH_TOKEN"]:
        raise ValueError("Twilio credentials not set in environment variables.")

    return config
