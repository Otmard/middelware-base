# app/services/payment_odoo_service.py

from datetime import datetime
from typing import Dict, Any

from app.services.base_odoo_service import BaseOdooService
from app.core.odoo import get_odoo_connection


class PaymentOdooService(BaseOdooService):
    def __init__(self, client=None):
        client = client or get_odoo_connection()
        super().__init__("account.payment.register", client)

    def register_payment(self, invoice: Dict[str, Any], journal_id: int):
        invoice_id = invoice["id"]

        payment_data = {
            "payment_type": "inbound",
            "communication": invoice["name"],
            "payment_date": datetime.now().strftime("%Y-%m-%d"),
            "amount": invoice["amount_total"],
            "currency_id": invoice["currency_id"][0],
            "partner_id": invoice["partner_id"][0],
            "journal_id": journal_id,
        }

        context = {
            "active_ids": [invoice_id],
            "active_model": "account.move",
            "active_id": invoice_id,
        }

        wizard_id = self.client.execute_kw(
            self.model_name,
            "create",
            args=[payment_data],
            kwargs={"context": context},
        )

        result = self.client.execute_kw(
            self.model_name,
            "action_create_payments",
            args=[[wizard_id]],
            kwargs={},
        )

        return result