# app/main.py

import logging
from fastapi import FastAPI
from app.core.config import settings
from app.core.logger import setup_logging
from app.core.middleware import logging_middleware
from app.routes import user, cliente
from app.schemas.error import ErrorResponse

app = FastAPI(
    title=settings.APP_NAME
)

from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="My API",
        version="1.0.0",
        description="API with global error schema",
        routes=app.routes,
    )

    # 🧠 FORZAR esquema de error global
    openapi_schema["components"]["schemas"]["ErrorResponse"] = {
        "type": "object",
        "properties": {
            "code": {"type": "string"},
            "message": {"type": "string"}
        },
        "required": ["code", "message"]
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


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
app.include_router(cliente.router)
# handlers globales

app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)