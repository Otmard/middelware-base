# app/core/logger.py
import logging
import sys
import json
from logging.handlers import RotatingFileHandler
from app.core.config import settings
import os

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # extras (contexto)
        for field in ["request_id", "path", "method", "status", "duration"]:
            if hasattr(record, field):
                log_record[field] = getattr(record, field)

        return json.dumps(log_record)


def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(settings.LOG_LEVEL)

    handlers = []

    # 🟢 consola
    console_handler = logging.StreamHandler(sys.stdout)

    if settings.ENV == "production":
        console_handler.setFormatter(JsonFormatter())
    else:
        console_handler.setFormatter(logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        ))

    handlers.append(console_handler)

    # 📁 asegurar carpeta logs existe
    os.makedirs("logs", exist_ok=True)

    # 🔵 archivo con rotación
    file_handler = RotatingFileHandler(
        "logs/app.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=5
    )

    file_handler.setFormatter(JsonFormatter())
    handlers.append(file_handler)

    logger.handlers = handlers

def get_logger(name: str):
    return logging.getLogger(name)