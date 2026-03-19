import json
import logging
import os
from datetime import datetime, timezone

from .config import LOG_FILE, LOG_LEVEL


def setup_logger() -> logging.Logger:
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    logger = logging.getLogger("triage")
    if logger.handlers:
        return logger

    logger.setLevel(LOG_LEVEL)
    handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    stream = logging.StreamHandler()

    formatter = logging.Formatter("%(message)s")
    handler.setFormatter(formatter)
    stream.setFormatter(formatter)

    logger.addHandler(handler)
    logger.addHandler(stream)
    return logger


def log_event(logger: logging.Logger, level: str, message: str, **fields: object) -> None:
    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "level": level,
        "message": message,
        **fields,
    }
    logger.log(getattr(logging, level, logging.INFO), json.dumps(record, ensure_ascii=False))

