# app/services/pago_service.py

import logging
from uuid import uuid4

from app.schemas.pago import PagoRequest, PagoDataResponse
from app.core.logger import get_logger

logger = get_logger(__name__)


class PagoService:
    def procesar_pago(self, request: PagoRequest) -> PagoDataResponse:
        logger.info(
            "Procesando pago",
            extra={
                "codigo_busqueda": request.codigo_busqueda,
                "id_transaccion": request.id_transaccion,
                "monto": request.monto_total
            }
        )

        # Generar UUID para id_txn_empresa
        id_txn_empresa = str(uuid4())

        logger.info(
            "Pago procesado",
            extra={"id_txn_empresa": id_txn_empresa}
        )

        return PagoDataResponse(
            codigo_busqueda=request.codigo_busqueda,
            id_txn_empresa=id_txn_empresa,
            id_txn_entidad=request.id_transaccion,
            # El resto de campos quedan como None
        )