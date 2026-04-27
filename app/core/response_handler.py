# app/core/response_handler.py

from typing import Any, Optional
from fastapi.responses import JSONResponse


def success_response(data: Any = None, code: str = "000", message: str = "PROCESO CONFORME") -> JSONResponse:
    return JSONResponse(
        status_code=200,
        content={
            "code": code,
            "message": message,
            "data": data
        }
    )


def build_response(code: str, message: str, data: Any = None) -> JSONResponse:
    return JSONResponse(
        status_code=200,
        content={
            "code": code,
            "message": message,
            "data": data
        }
    )
