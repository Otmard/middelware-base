# app/services/pago_service.py

import json
import logging
from app.schemas.pago import PagoRequest, PagoDataResponse
from app.core.logger import get_logger
from app.database.audit_repository import AuditRepository

logger = get_logger(__name__)


class PagoService:
    def __init__(self):
        self.audit_repo = AuditRepository()

    async def procesar_pago(self, request: PagoRequest, request_dict: dict) -> PagoDataResponse:
        request_dict_clean = {k: v for k, v in request_dict.items() if v is not None}
        
        audit = await self.audit_repo.create_audit(
            endpoint="/pagos/procesar",
            method="POST",
            request_body=request_dict_clean,
            response_body={},
            status_code=200,
        )
        
        await self.audit_repo.create_pago_request(audit.id, request_dict_clean)
        
        id_txn_empresa = await self.audit_repo.get_next_pago_id()
        
        response_data = {
            "id_txn_entidad": request.id_transaccion,
            "codigo_busqueda": request.codigo_busqueda,
            "id_txn_empresa": id_txn_empresa,
        }
        
        await self.audit_repo.create_pago_response(audit.id, response_data, id_txn_empresa)
        
        logger.info(
            "Pago procesado",
            extra={"id_txn_empresa": id_txn_empresa, "audit_id": audit.id}
        )

        return PagoDataResponse(
            codigo_busqueda=request.codigo_busqueda,
            id_txn_empresa=str(id_txn_empresa),
            id_txn_entidad=request.id_transaccion,
        )