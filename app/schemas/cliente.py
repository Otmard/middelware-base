# app/schemas/cliente.py

from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field


class Pago(BaseModel):
    numeroCuota: int = Field(..., description="Correlativo de la cuota")
    detalleCuota: str = Field(..., description="Descripción de la cuota/factura")
    fechaVencimiento: Optional[str] = Field(None, description="Fecha límite de pago (AAAAMMDD)")
    importeCuota: Decimal = Field(..., decimal_places=2, description="Monto total de la cuota")
    importeMinimoCuota: Decimal = Field(default=Decimal("0.00"), decimal_places=2, description="Monto mínimo a pagar")
    moraCuota: Decimal = Field(default=Decimal("0.00"), decimal_places=2, description="Monto de mora aplicado")
    importeComision: Decimal = Field(default=Decimal("0.00"), decimal_places=2, description="Comisión por cuota")


class ClienteRequest(BaseModel):
    CodServicio: str = Field(..., min_length=3, max_length=3, description="Código del servicio")
    CodigoBusqueda: str = Field(..., min_length=1, max_length=14, description="Código único del cliente")
