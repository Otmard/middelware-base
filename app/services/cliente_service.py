# app/services/cliente_service.py

from decimal import Decimal
from typing import Any, Dict, List

from app.core.exceptions import AppException
from app.core.logger import get_logger
from app.core.error_registry import ErrorRegistry
from app.core.odoo import get_odoo_connection
from app.schemas.cliente import (
    ClienteRequest,
    Pago,
    ClienteStandardResponse,
    ClienteDataResponse,
)
from app.services.partner_odoo_service import PartnersOdooService
from app.services.lead_odoo_service import LeadsOdooService
from app.services.invoice_odoo_service import InvoicesOdooService
from app.database.audit_repository import AuditRepository

logger = get_logger(__name__)


class ClienteService:
    COD_SERVICIO_BY_ID = "001"
    COD_SERVICIO_BY_VAT = "002"
    COD_SERVICIO_BY_LEAD = "003"

    def __init__(self):
        self._client = get_odoo_connection()
        self.partner_service = PartnersOdooService(client=self._client)
        self.lead_service = LeadsOdooService(client=self._client)
        self.invoice_service = InvoicesOdooService(client=self._client)
        self.audit_repo = AuditRepository()

    def _get_invoices_by_partner(self, partner_id: int) -> List[Dict[str, Any]]:
        return self.invoice_service.get_invoices_by_partner(
            partner_id=partner_id,
            state="posted",
            move_type="out_invoice",
            payment_state="not_paid",
            fields=[
                "id",
                "name",
                "invoice_date_due",
                "amount_total"
            ]
        )

    def _build_pagos_from_invoices(self, invoices: List[Dict[str, Any]]) -> List[Pago]:
        pagos = []
        for idx, inv in enumerate(invoices):
            pagos.append(Pago(
                numeroCuota=idx,
                detalleCuota=inv.get("name", ""),
                fechaVencimiento=self._format_date_odoo(inv.get("invoice_date_due")),
                importeCuota=Decimal(str(inv.get("amount_total", 0))),
                importeMinimoCuota=Decimal("0.00"),
                moraCuota=Decimal("0.00"),
                importeComision=Decimal("0.00")
            ))
        return pagos

    def _format_date_odoo(self, date_value: Any) -> str:
        if not date_value:
            return ""
        if isinstance(date_value, str):
            return date_value.replace("-", "")
        return str(date_value)

    def _calculate_total_debt(self, invoices: List[Dict[str, Any]]) -> Decimal:
        return sum(
            Decimal(str(inv.get("amount_total", 0)))
            for inv in invoices
        )

    async def _save_audit(self, endpoint: str, method: str, response_dict: dict, request_dict: dict = None):
        from decimal import Decimal
        def convert_value(v):
            if isinstance(v, Decimal):
                return str(v)
            if isinstance(v, (list, tuple)):
                return [convert_value(i) for i in v]
            if isinstance(v, dict):
                return {kk: convert_value(vv) for kk, vv in v.items()}
            return v
        
        try:
            request_dict_clean = {k: convert_value(v) for k, v in request_dict.items()} if request_dict else {}
            
            response_for_audit = {k: convert_value(v) for k, v in response_dict.items()}
            
            audit = await self.audit_repo.create_audit(
                endpoint=endpoint,
                method=method,
                request_body=request_dict_clean,
                response_body=response_for_audit,
                status_code=200,
            )
            
            if request_dict_clean:
                await self.audit_repo.create_cliente_request(audit.id, request_dict_clean)
            
            data = response_dict.get("data", {})
            if data:
                await self.audit_repo.create_cliente_response(audit.id, data)
                
            logger.info("Audit saved", extra={"audit_id": audit.id})
        except Exception as e:
            import traceback
            logger.error(f"Error saving audit: {e}", extra={"trace": traceback.format_exc()})

    async def _build_success_response(
        self,
        codigo_busqueda: str,
        cod_servicio: str,
        partner_data: Dict[str, Any],
        invoices: List[Dict[str, Any]] = None,
        request_dict: dict = None,
    ) -> ClienteStandardResponse:
        nombre = partner_data.get("name", "")
        invoices = invoices or []
        total_debt = self._calculate_total_debt(invoices)
        pagos = self._build_pagos_from_invoices(invoices)

        logger.info(
            "Building success response",
            extra={"codigo": codigo_busqueda, "nombre": nombre, "total_deuda": str(total_debt), "nro_facturas": len(invoices)}
        )

        data = ClienteDataResponse(
            codigoBusqueda=codigo_busqueda,
            codigoServicio=cod_servicio,
            importeAdeudado=str(total_debt),
            importeMinimo="0.00",
            importeComision="0.00",
            nombreCliente=nombre.upper(),
            pagos=pagos
        )

        response_dict = {
            "code": "000",
            "message": "PROCESO CONFORME",
            "data": data.model_dump()
        }
        
        await self._save_audit("/api/consulta-cliente", "POST", response_dict, request_dict)

        return ClienteStandardResponse(code="000", message="PROCESO CONFORME", data=data)

    async def _build_not_found_response(
        self,
        codigo_busqueda: str,
        cod_servicio: str,
        request_dict: dict = None,
    ) -> ClienteStandardResponse:
        logger.warning("Cliente not found", extra={"codigo": codigo_busqueda})

        data = ClienteDataResponse(
            codigoBusqueda=codigo_busqueda,
            codigoServicio=cod_servicio,
            importeAdeudado="0.00",
            importeMinimo="0.00",
            importeComision="0.00",
            nombreCliente="",
            pagos=[]
        )

        response_dict = {
            "code": "301",
            "message": "CÓDIGO DE DEPOSITANTE NO EXISTE",
            "data": data.model_dump()
        }
        
        await self._save_audit("/api/consulta-cliente", "POST", response_dict, request_dict)

        return ClienteStandardResponse(code="301", message="CÓDIGO DE DEPOSITANTE NO EXISTE", data=data)

    def _get_partner_by_id(self, codigo_busqueda: str) -> Dict[str, Any]:
        partner_id = int(codigo_busqueda)
        result = self.partner_service.get(
            record_ids=[partner_id],
            fields=["id", "name", "ref", "vat", "email", "phone"]
        )
        return result[0] if result else None

    def _get_partner_by_vat(self, codigo_busqueda: str) -> Dict[str, Any]:
        result = self.partner_service.search_read(
            domain=[["vat", "=", codigo_busqueda]],
            fields=["id", "name", "ref", "vat", "email", "phone"],
            limit=1
        )
        return result[0] if result else None

    def _get_partner_by_lead(self, codigo_busqueda: str) -> Dict[str, Any]:
        lead_id = int(codigo_busqueda)
        lead = self.lead_service.get(
            record_ids=[lead_id],
            fields=["id", "name", "partner_id"]
        )
        if lead and lead[0].get("partner_id"):
            partner_id = lead[0]["partner_id"][0]
            return self._get_partner_by_id(str(partner_id))
        return None

    async def consultar_cliente(self, request: ClienteRequest, request_dict: dict) -> ClienteStandardResponse:
        codigo_busqueda = request.CodigoBusqueda
        cod_servicio = request.CodServicio

        logger.info(
            "Consultando cliente",
            extra={"codigo": codigo_busqueda, "servicio": cod_servicio}
        )

        try:
            partner = None

            if cod_servicio == self.COD_SERVICIO_BY_ID:
                try:
                    partner = self._get_partner_by_id(codigo_busqueda)
                except (ValueError, TypeError):
                    partner = None

            elif cod_servicio == self.COD_SERVICIO_BY_VAT:
                partner = self._get_partner_by_vat(codigo_busqueda)

            elif cod_servicio == self.COD_SERVICIO_BY_LEAD:
                try:
                    partner = self._get_partner_by_lead(codigo_busqueda)
                except (ValueError, TypeError):
                    partner = None

            else:
                logger.warning("CodServicio no válido", extra={"cod_servicio": cod_servicio})

            if not partner:
                return await self._build_not_found_response(codigo_busqueda, cod_servicio, request_dict)

            invoices = self._get_invoices_by_partner(partner["id"])

            return await self._build_success_response(codigo_busqueda, cod_servicio, partner, invoices, request_dict)

        except AppException:
            raise
        except Exception as e:
            logger.error("Error consultando cliente", extra={"error": str(e), "codigo": codigo_busqueda})
            raise AppException(ErrorRegistry.ODOO_CONNECTION_FAILED)
