# app/core/error_handler.py

import logging
from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.exceptions import AppException
from app.core.error_registry import ErrorRegistry

logger = logging.getLogger("error_handler")


async def app_exception_handler(request: Request, exc: AppException):
    error = exc.error

    logger.warning(
        "app error",
        extra={
            "path": request.url.path,
            "method": request.method,
            "code": error.code,
            "status": error.status,
        },
    )

    return JSONResponse(
        status_code=error.status,
        content={"code": error.code, "message": error.message, "data": None},
    )


async def global_exception_handler(request: Request, exc: Exception):
    err = ErrorRegistry.INTERNAL_ERROR

    logger.error(
        "unexpected error",
        exc_info=True,
        extra={"path": request.url.path, "code": err.code},
    )

    return JSONResponse(
        status_code=err.status,
        content={"code": err.code, "message": err.message, "data": None},
    )

    return JSONResponse(
        status_code=exc.error.status,
        content={"code": exc.error.code, "message": exc.error.message, "data": None},
    )


async def global_exception_handler(request: Request, exc: Exception):
    err = ErrorRegistry.INTERNAL_ERROR

    logger.error(
        "unexpected error",
        exc_info=True,
        extra={"path": request.url.path, "code": err.code},
    )

    return JSONResponse(
        status_code=err.status,
        content={"code": err.code, "message": err.message, "data": None},
    )
