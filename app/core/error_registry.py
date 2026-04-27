# app/core/error_registry.py

from dataclasses import dataclass

from app.schemas.error import ErrorResponse

@dataclass(frozen=True)
class ErrorDetail:
    code: str
    status: int
    message: str


class ErrorRegistry:
    # Auth
    INVALID_CREDENTIALS = ErrorDetail(
        code="INVALID_CREDENTIALS",
        status=401,
        message="Invalid credentials"
    )

    UNAUTHORIZED = ErrorDetail(
        code="UNAUTHORIZED",
        status=401,
        message="Unauthorized"
    )

    TOKEN_EXPIRED = ErrorDetail(
        code="TOKEN_EXPIRED",
        status=401,
        message="Token expired"
    )

    # Users
    USER_NOT_FOUND = ErrorDetail(
        code="USER_NOT_FOUND",
        status=404,
        message="User not found"
    )

    USER_ALREADY_EXISTS = ErrorDetail(
        code="USER_ALREADY_EXISTS",
        status=409,
        message="User already exists"
    )

    # General
    BAD_REQUEST = ErrorDetail(
        code="BAD_REQUEST",
        status=400,
        message="Bad request"
    )

    INTERNAL_ERROR = ErrorDetail(
        code="INTERNAL_ERROR",
        status=500,
        message="Internal server error"
    )

    # External
    ODOO_CONNECTION_FAILED = ErrorDetail(
        code="ODOO_CONNECTION_FAILED",
        status=502,
        message="Odoo connection failed"
    )

    # Cliente
    CLIENTE_NOT_FOUND = ErrorDetail(
        code="CLIENTE_NOT_FOUND",
        status=404,
        message="Cliente no encontrado"
    )

    CLIENTE_INVALID_PARAMS = ErrorDetail(
        code="CLIENTE_INVALID_PARAMS",
        status=400,
        message="Parámetros inválidos"
    )
    
    EXTERNAL_SERVICE_ERROR = ErrorDetail(
        code="EXTERNAL_SERVICE_ERROR",
        status=502,
        message="Error de conexión con servicio externo"
    )
    
    REDIS_CONNECTION_FAILED = ErrorDetail(
        code="REDIS_CONNECTION_FAILED",
        status=502,
        message="Error de conexión con Redis"
    )
    REDIS_OPERATION_FAILED = ErrorDetail(
    code="REDIS_OPERATION_FAILED",
    status=500,
    message="Error en operación con Redis"
)
    
def build_error_responses(*errors):
    responses = {}

    for err in errors:
        responses[err.status] = {
            "model": ErrorResponse,
            "description": err.message,
            "content": {
                "application/json": {
                    "example": {
                        "code": err.code,
                        "message": err.message
                    }
                }
            }
        }

    return responses