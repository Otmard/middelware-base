# app/services/invoice_odoo_service.py

from typing import Any, Dict, List, Optional

from app.core.logger import get_logger
from app.core.odoo import get_odoo_connection
from app.services.base_odoo_service import BaseOdooService


class InvoicesOdooService(BaseOdooService):
    def __init__(self, client=None):
        client = client or get_odoo_connection()
        super().__init__("account.move", client)
        self.logger = get_logger(__name__)

    def get_invoices_by_partner(
        self,
        partner_id: int,
        state: str = "posted",
        move_type: str = "out_invoice",
        payment_state: str = "not_paid",
        fields: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        self.logger.debug("Getting unpaid invoices by partner", extra={"partner_id": partner_id})
        domain = [
            ["partner_id", "=", partner_id],
            ["state", "=", state],
            ["move_type", "=", move_type],
            ["payment_state", "=", payment_state],
        ]
        
        default_fields = ["id", "name", "invoice_date_due", "amount_total"]
        return self.search_read(
            domain=domain,
            fields=fields or default_fields,
            order="id desc",
        )

    def get_total_debt_by_partner(
        self,
        partner_id: int,
        state: str = "posted",
        move_type: str = "out_invoice"
    ) -> float:
        invoices = self.get_invoices_by_partner(
            partner_id=partner_id,
            state=state,
            move_type=move_type,
            fields=["amount_residual"]
        )
        return sum(inv.get("amount_residual", 0) for inv in invoices)

