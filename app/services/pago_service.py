# app/services/pago_service.py

import logging
from app.schemas.pago import PagoRequest, PagoDataResponse
from app.core.logger import get_logger
from app.database.audit_repository import AuditRepository
from app.services.invoice_odoo_service import InvoicesOdooService
from app.services.payment_odoo_service import PaymentOdooService

logger = get_logger(__name__)


class PagoService:
    def __init__(self):
        self.audit_repo = AuditRepository()
        self.invoice_service = InvoicesOdooService()
        self.payment_service = PaymentOdooService()

    async def procesar_pago(
        self, request: PagoRequest, request_dict: dict
    ) -> PagoDataResponse:
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

        ids_numero_cuota = []
        for det in request.detalles:
            ids_numero_cuota.append(det.numero_cuota)

        data_invoice = self.invoice_service.search_read(
            domain=[
                ["id", "in", ids_numero_cuota],
                ["state", "=", "posted"],
                ["move_type", "=", "out_invoice"],
                ["payment_state", "=", "not_paid"],
            ],
            fields=[
                "id",
                "name",
                "amount_total",
                "currency_id",
                "partner_id",
                "amount_residual",
            ],
        )
        for invoice in data_invoice:

            if invoice.get("amount_residual", 0) <= 0:
                continue

            self.payment_service.register_payment(invoice=invoice, journal_id=7)


        pago_response = PagoDataResponse(
            codigo_busqueda=request.codigo_busqueda,
            id_txn_empresa=str(id_txn_empresa),
            id_txn_entidad=request.id_transaccion,
            casa_matriz="MAPLENET COMUNICACIONES S.A.",
            direccion="Esquina calle 20 de calacoto y Gral. Inofuentes #1375 ",
            telefono="2779818",
            ciudad_dosificacion="La Paz",
            nit="550267024",
            nro_autorizacion="25A69AACD67CF02AACFDF044419C9FBE8C0E9E06A70E05AFD4FDBAF74",
            razon_social="MAPLENET COMUNICACIONES S.A.",
            nro_factura=str(ids_numero_cuota),
            detalle_factura="pagos de facturas" + str(data_invoice),
        )

        await self.audit_repo.create_pago_response(
            audit.id, pago_response.model_dump(exclude_none=False), id_txn_empresa
        )

        logger.info(
            "Pago procesado",
            extra={"id_txn_empresa": id_txn_empresa, "audit_id": audit.id},
        )

        return pago_response
