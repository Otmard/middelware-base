# app/services/lead_odoo_service.py

from typing import Any, Dict, List, Optional

from app.core.logger import get_logger
from app.core.odoo import get_odoo_connection
from app.services.base_odoo_service import BaseOdooService


class LeadsOdooService(BaseOdooService):
    def __init__(self, client=None):
        client = client or get_odoo_connection()
        super().__init__("crm.lead", client)
        self.logger = get_logger(__name__)

    def get_lead_with_partner(
        self,
        lead_id: int,
        partner_fields: Optional[List[str]] = None
    ) -> Optional[Dict[str, Any]]:
        self.logger.debug("Getting lead with partner data", extra={"lead_id": lead_id})
        leads = self.search_read(
            domain=[["id", "=", lead_id]],
            fields=["id", "name", "partner_id"],
            limit=1
        )
        
        if not leads:
            return None
        
        lead = leads[0]
        partner_id = lead.get("partner_id")
        
        if partner_id:
            from app.services.partner_odoo_service import PartnersOdooService
            partner_service = PartnersOdooService(client=self.client)
            partner = partner_service.get(
                record_ids=[partner_id[0] if isinstance(partner_id, list) else partner_id],
                fields=partner_fields or ["id", "name", "ref", "vat", "email", "phone"]
            )
            lead["partner_data"] = partner[0] if partner else None
        
        return lead
