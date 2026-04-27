# app/schemas/cliente.py

from decimal import Decimal
from typing import List, Optional, Generic, TypeVar, Any

from pydantic import BaseModel, Field, ConfigDict

T = TypeVar('T')


class Pago(BaseModel):
    numeroCuota: int = Field(..., description="Correlativo de la cuota")
    detalleCuota: str = Field(..., description="Descripción de la cuota/factura")
    fechaVencimiento: Optional[str] = Field(None, description="Fecha límite de pago (AAAAMMDD)")
    importeCuota: Decimal = Field(..., decimal_places=2, description="Monto total de la cuota")
    importeMinimoCuota: Decimal = Field(default=Decimal("0.00"), decimal_places=2, description="Monto mínimo a pagar")
    moraCuota: Decimal = Field(default=Decimal("0.00"), decimal_places=2, description="Monto de mora aplicado")
    importeComision: Decimal = Field(default=Decimal("0.00"), decimal_places=2, description="Comisión por cuota")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "numeroCuota": 0,
                "detalleCuota": "FACT-001",
                "fechaVencimiento": "20260427",
                "importeCuota": "100.00",
                "importeMinimoCuota": "0.00",
                "moraCuota": "0.00",
                "importeComision": "0.00"
            }
        }
    )


class ClienteRequest(BaseModel):
    CodServicio: str = Field(..., min_length=3, max_length=3, description="Código del servicio")
    CodigoBusqueda: str = Field(..., min_length=1, max_length=14, description="Código único del cliente")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "CodServicio": "001",
                "CodigoBusqueda": "1231231231"
            }
        }
    )


class ClienteDataResponse(BaseModel):
    codigoBusqueda: str = Field(..., description="Código de búsqueda del cliente")
    codigoServicio: str = Field(..., description="Código del servicio")
    importeAdeudado: str = Field(..., description="Importe total adeudado")
    importeMinimo: str = Field(..., description="Importe mínimo a pagar")
    importeComision: str = Field(..., description="Importe de comisión")
    nombreCliente: str = Field(..., description="Nombre del cliente")
    pagos: List[Pago] = Field(default_factory=list, description="Lista de pagos/cuotas")


class StandardResponse(BaseModel, Generic[T]):
    code: str = Field(..., description="Código de respuesta")
    message: str = Field(..., description="Mensaje descriptivo")
    data: Optional[T] = Field(default=None, description="Datos de respuesta")


class ClienteStandardResponse(StandardResponse[ClienteDataResponse]):
    data: Optional[ClienteDataResponse] = Field(default=None, description="Datos del cliente")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "code": "000",
                "message": "PROCESO CONFORME",
                "data": {
                    "codigoBusqueda": "1",
                    "codigoServicio": "001",
                    "importeAdeudado": "0",
                    "importeMinimo": "0.00",
                    "importeComision": "0.00",
                    "nombreCliente": "MAPLENET COMUNICACIONES S.A.",
                    "pagos": []
                }
            }
        }
    )
