# app/routes/cliente.py

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.core.logger import get_logger
from app.schemas.cliente import ClienteRequest
from app.services.cliente_service import ClienteService

router = APIRouter(prefix="/api", tags=["Clientes"])
logger = get_logger(__name__)


def get_cliente_service():
    return ClienteService()


@router.post(
    "/consulta-cliente",
    status_code=status.HTTP_200_OK,
)
def consultar_cliente(
    payload: ClienteRequest,
    service: ClienteService = Depends(get_cliente_service),
) -> JSONResponse:
    logger.info(
        "Received consulta-cliente request",
        extra={"servicio": payload.CodServicio}
    )
    return service.consultar_cliente(payload)
