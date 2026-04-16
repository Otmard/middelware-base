# app/services/partner_odoo_service.py

from app.core.logger import get_logger
from app.core.odoo import get_odoo_connection
from app.services.base_odoo_service import BaseOdooService


class PartnersOdooService(BaseOdooService):
    def __init__(self, client=None):
        client = client or get_odoo_connection()
        super().__init__("res.partner", client)
        self.logger = get_logger(__name__)
