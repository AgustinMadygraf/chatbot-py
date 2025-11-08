"""
Path: src/shared/logger_rasa_v0.py
"""

import logging
import coloredlogs
from src.shared.config import get_config

def get_logger(name="rasa-bot"):
    "Configura y devuelve un logger con formato estilo Rasa usando coloredlogs."
    config = get_config()
    log_level = config.get("LOG_LEVEL", "DEBUG").upper()
    logger = logging.getLogger(name)
    # Evita agregar múltiples handlers si ya existe uno
    if not logger.handlers:
        # Formato similar al de Rasa
        fmt = "%(asctime)s %(levelname)-8s %(name)s  - %(message)s"
        datefmt = "%Y-%m-%d %H:%M:%S"
        coloredlogs.install(
            level=log_level,
            logger=logger,
            fmt=fmt,
            datefmt=datefmt,
            isatty=True
        )
        logger.setLevel(getattr(logging, log_level, logging.DEBUG))
    return logger
