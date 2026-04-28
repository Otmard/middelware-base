# app/routes/pago.py

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.core.logger import get_logger
from app.schemas.pago import PagoRequest, PagoStandardResponse, PagoDataResponse
from app.services.pago_service import PagoService
import json

router = APIRouter(prefix="/pagos", tags=["Pagos"])
logger = get_logger(__name__)


def get_pago_service():
    return PagoService()


@router.post(
    "/procesar",
    response_model=PagoStandardResponse,
    status_code=status.HTTP_200_OK,
)
async def procesar_pago(
    payload: PagoRequest,
    service: PagoService = Depends(get_pago_service),
) -> PagoStandardResponse:
    logger.info(
        "Received procesar-pago request",
        extra={"codigo_busqueda": payload.codigo_busqueda}
    )

    request_dict = payload.model_dump()
    
    data = await service.procesar_pago(payload, request_dict)
    
    return PagoStandardResponse(
        code="000",
        message="PROCESO CONFORME",
        data=data
    )