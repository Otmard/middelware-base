# app/schemas/cliente.py

from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field


class Cabecera(BaseModel):
    Entidad: str = Field(..., description="Identificador de la entidad (BCP)")
    Usuario: str = Field(..., description="Usuario autorizado")
    Contraseña: str = Field(..., description="Credenciales de acceso")


class CargaUtilRequest(BaseModel):
    CodServicio: str = Field(..., min_length=3, max_length=3, description="Código del servicio")
    CodigoBusqueda: str = Field(..., min_length=1, max_length=14, description="Código único del cliente")


class ClienteRequest(BaseModel):
    Cabecera: Cabecera
    CargaUtil: CargaUtilRequest


class Pago(BaseModel):
    NumeroCuota: int = Field(..., description="Correlativo de la cuota")
    DetalleCuota: str = Field(..., description="Descripción de la cuota/factura")
    FechaVencimiento: Optional[str] = Field(None, description="Fecha límite de pago (AAAAMMDD)")
    ImporteCuota: Decimal = Field(..., decimal_places=2, description="Monto total de la cuota")
    ImporteMinimoCuota: Decimal = Field(default=Decimal("0.00"), decimal_places=2, description="Monto mínimo a pagar")
    MoraCuota: Decimal = Field(default=Decimal("0.00"), decimal_places=2, description="Monto de mora aplicado")
    ImporteComision: Decimal = Field(default=Decimal("0.00"), decimal_places=2, description="Comisión por cuota")


class HeadersResponse(BaseModel):
    CodError: str = Field(..., description="Código de respuesta. 000 indica éxito")
    Descripcion: str = Field(..., description="Mensaje descriptivo del código de error")


class CargaUtilResponse(BaseModel):
    CodigoBusqueda: str
    CodigoServicio: str
    ImporteAdeudado: Decimal = Field(default=Decimal("0.00"), decimal_places=2)
    ImporteMinimo: Decimal = Field(default=Decimal("0.00"), decimal_places=2)
    ImporteComision: Decimal = Field(default=Decimal("0.00"), decimal_places=2)
    NombreCliente: str = Field(default="")
    Pagos: List[Pago] = Field(default_factory=list)


class ClienteResponse(BaseModel):
    Headers: HeadersResponse
    CargaUtil: CargaUtilResponse
