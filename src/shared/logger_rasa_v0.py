"""
Path: src/shared/logger_rasa_v0.py
"""

import logging

import coloredlogs

from src.shared.config import get_config


class TruncatingColoredFormatter(coloredlogs.ColoredFormatter):
    """Formatter que replica la estética de Rasa CLI y recorta mensajes extensos."""

    def __init__(self, *args, max_length=None, **kwargs):
        self.max_length = max_length
        super().__init__(*args, **kwargs)

    def format(self, record):
        original_msg, original_args = record.msg, record.args
        if self.max_length and self.max_length > 0:
            message = record.getMessage()
            if isinstance(message, str) and len(message) > self.max_length:
                ellipsis = "…"
                cutoff = max(self.max_length - len(ellipsis), 1)
                record.msg = f"{message[:cutoff].rstrip()}{ellipsis}"
                record.args = ()
        try:
            return super().format(record)
        finally:
            record.msg, record.args = original_msg, original_args


def get_logger(name="rasa-bot"):
    "Configura y devuelve un logger con formato estilo Rasa usando coloredlogs."
    config = get_config()
    logger = logging.getLogger(name)
    raw_max_length = config.get("LOG_MESSAGE_MAX_LENGTH", 160)
    try:
        max_length = int(raw_max_length)
    except (TypeError, ValueError):
        max_length = 160
    if max_length <= 0:
        max_length = None
    if not logger.handlers:
        # Formato similar al de Rasa
        fmt = "%(asctime)s %(levelname)-8s %(name)-24s - %(message)s"
        datefmt = "%Y-%m-%d %H:%M:%S"
        coloredlogs.install(
            level="DEBUG",
            logger=logger,
            fmt=fmt,
            datefmt=datefmt,
            isatty=True,
        )
        formatter = TruncatingColoredFormatter(
            fmt=fmt,
            datefmt=datefmt,
            level_styles=coloredlogs.DEFAULT_LEVEL_STYLES,
            field_styles=coloredlogs.DEFAULT_FIELD_STYLES,
            max_length=max_length,
        )
        for handler in logger.handlers:
            handler.setFormatter(formatter)
        logger.propagate = False
    else:
        for handler in logger.handlers:
            formatter = getattr(handler, "formatter", None)
            if isinstance(formatter, TruncatingColoredFormatter):
                formatter.max_length = max_length
    logger.setLevel(logging.DEBUG)
    return logger
