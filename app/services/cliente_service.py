# app/services/cliente_service.py

from decimal import Decimal
from typing import Any, Dict, Optional

from app.core.exceptions import AppException
from app.core.logger import get_logger
from app.core.error_registry import ErrorRegistry
from app.core.odoo import get_odoo_connection
from app.schemas.cliente import (
    ClienteRequest,
    ClienteResponse,
    CargaUtilResponse,
    HeadersResponse,
)
from app.services.partner_odoo_service import PartnersOdooService
from app.services.lead_odoo_service import LeadsOdooService

logger = get_logger(__name__)


class ClienteService:
    COD_SERVICIO_BY_ID = "001"
    COD_SERVICIO_BY_VAT = "002"
    COD_SERVICIO_BY_LEAD = "003"

    def __init__(self):
        self._client = get_odoo_connection()
        self.partner_service = PartnersOdooService(client=self._client)
        self.lead_service = LeadsOdooService(client=self._client)

    def _build_success_response(
        self,
        codigo_busqueda: str,
        cod_servicio: str,
        partner_data: Dict[str, Any],
    ) -> ClienteResponse:
        nombre = partner_data.get("name", "")
        logger.info("Building success response", extra={"codigo": codigo_busqueda, "nombre": nombre})

        return ClienteResponse(
            Headers=HeadersResponse(
                CodError="000",
                Descripcion="PROCESO CONFORME"
            ),
            CargaUtil=CargaUtilResponse(
                CodigoBusqueda=codigo_busqueda,
                CodigoServicio=cod_servicio,
                ImporteAdeudado=Decimal("0.00"),
                ImporteMinimo=Decimal("0.00"),
                ImporteComision=Decimal("0.00"),
                NombreCliente=nombre.upper(),
                Pagos=[]
            )
        )

    def _build_not_found_response(
        self,
        codigo_busqueda: str,
        cod_servicio: str,
    ) -> ClienteResponse:
        logger.warning("Cliente not found", extra={"codigo": codigo_busqueda})
        return ClienteResponse(
            Headers=HeadersResponse(
                CodError="301",
                Descripcion="CÓDIGO DE DEPOSITANTE NO EXISTE"
            ),
            CargaUtil=CargaUtilResponse(
                CodigoBusqueda=codigo_busqueda,
                CodigoServicio=cod_servicio,
                ImporteAdeudado=Decimal("0.00"),
                ImporteMinimo=Decimal("0.00"),
                ImporteComision=Decimal("0.00"),
                NombreCliente="",
                Pagos=[]
            )
        )

    def consultar_cliente(self, request: ClienteRequest) -> ClienteResponse:
        codigo_busqueda = request.CargaUtil.CodigoBusqueda
        cod_servicio = request.CargaUtil.CodServicio

        logger.info(
            "Consultando cliente",
            extra={"codigo": codigo_busqueda, "servicio": cod_servicio}
        )

        try:
            partner = None
            fields = ["id", "name", "ref", "vat", "email", "phone"]

            if cod_servicio == self.COD_SERVICIO_BY_ID:
                try:
                    partner_id = int(codigo_busqueda)
                    result = self.partner_service.get(record_ids=[partner_id], fields=fields)
                    partner = result[0] if result else None
                except (ValueError, TypeError):
                    partner = None

            elif cod_servicio == self.COD_SERVICIO_BY_VAT:
                result = self.partner_service.search_read(
                    domain=[["vat", "=", codigo_busqueda]],
                    fields=fields,
                    limit=1
                )
                partner = result[0] if result else None

            elif cod_servicio == self.COD_SERVICIO_BY_LEAD:
                try:
                    lead_id = int(codigo_busqueda)
                    lead = self.lead_service.get(record_ids=[lead_id], fields=["id", "name", "partner_id"])
                    if lead and lead[0].get("partner_id"):
                        partner_id = lead[0]["partner_id"][0]
                        result = self.partner_service.get(record_ids=[partner_id], fields=fields)
                        partner = result[0] if result else None
                except (ValueError, TypeError):
                    partner = None

            else:
                logger.warning("CodServicio no válido", extra={"cod_servicio": cod_servicio})

            if not partner:
                return self._build_not_found_response(codigo_busqueda, cod_servicio)

            return self._build_success_response(codigo_busqueda, cod_servicio, partner)

        except AppException:
            raise
        except Exception as e:
            logger.error("Error consultando cliente", extra={"error": str(e), "codigo": codigo_busqueda})
            raise AppException(ErrorRegistry.ODOO_CONNECTION_FAILED)
