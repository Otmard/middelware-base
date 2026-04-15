# app/main.py

import logging
from fastapi import FastAPI
from app.core.config import settings
from app.core.logger import setup_logging
from app.core.middleware import logging_middleware
from app.routes import user

app = FastAPI(
    title=settings.APP_NAME
)
from app.core.error_handler import (
    app_exception_handler,
    global_exception_handler
)
from app.core.exceptions import AppException

# setup logging
setup_logging()

# evitar duplicados de uvicorn
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

# middleware
app.middleware("http")(logging_middleware)
app.include_router(user.router)
# handlers globales

app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)