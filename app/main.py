# app/main.py

import logging
from fastapi import FastAPI
from app.core.config import settings
from app.core.logger import setup_logging
from app.core.middleware import logging_middleware
from app.routes import test_auth_router, user, cliente, pago
from app.schemas.error import ErrorResponse
from contextlib import asynccontextmanager
from app.core.redis import redis_client

app = FastAPI(
    title=settings.APP_NAME
)

from fastapi.openapi.utils import get_openapi
from app.schemas.cliente import StandardResponse

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 🔥 STARTUP
    await redis_client.connect()

    yield

    # 🔥 SHUTDOWN
    await redis_client.disconnect()


app = FastAPI(lifespan=lifespan)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="My API",
        version="1.0.0",
        description="API with global error schema",
        routes=app.routes,
    )

    # Agregar ejemplos completos a las rutas
    if "/pagos/procesar" in openapi_schema["paths"]:
        openapi_schema["paths"]["/pagos/procesar"]["post"]["responses"]["200"] = {
            "description": "Pago procesado correctamente",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/PagoStandardResponse"},
                    "example": {
                        "code": "000",
                        "message": "PROCESO CONFORME",
                        "data": {
                            "codigo_busqueda": "1231231231",
                            "id_txn_empresa": "550e8400-e29b-41d4-a716-446655440000",
                            "id_txn_entidad": 123456789,
                            "razon_social": None,
                            "casa_matriz": None,
                            "direccion": None,
                            "telefono": None,
                            "ciudad_dosificacion": None,
                            "nit": None,
                            "nro_autorizacion": None,
                            "nro_factura": None,
                            "actividad_economica": None,
                            "hora_emision_fac": None,
                            "fecha_emision_fac": None,
                            "detalle_factura": None,
                            "importe_original": None,
                            "tipo_cambio": None,
                            "importe_total": None,
                            "literal_importe_total": None,
                            "codigo_control": None,
                            "fecha_lim_emision": None,
                            "cadena_qr": None
                        }
                    }
                }
            }
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
app.include_router(test_auth_router.router)
app.include_router(pago.router)
# handlers globales

app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)