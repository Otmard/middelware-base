# app/schemas/pago.py

from uuid import uuid4
from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict


class DetallePagoRequest(BaseModel):
    numero_cuota: int = Field(..., description="Número de cuota")
    importe_cuota: float = Field(..., description="Importe de la cuota")


class PagoRequest(BaseModel):
    id_transaccion: int = Field(..., description="ID único de transacción generado por la entidad bancaria")
    fecha_pago: str = Field(..., pattern="^[0-9]{8}$", description="Fecha del pago en formato AAAAMMDD")
    codigo_busqueda: str = Field(..., max_length=14, description="Código identificador del cliente")
    monto_total: float = Field(..., description="Monto total cancelado")
    nombre_factura: Optional[str] = Field(None, max_length=40, description="Nombre para la factura")
    nit: Optional[str] = Field(None, max_length=8, description="NIT del cliente")
    lugar_pago: Optional[str] = Field(None, max_length=10, description="Lugar donde se realizó el pago")
    detalles: Optional[List[DetallePagoRequest]] = Field(default_factory=list, description="Detalles del pago")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id_transaccion": 123456789,
                "fecha_pago": "20260427",
                "codigo_busqueda": "1231231231",
                "monto_total": 100.50,
                "nombre_factura": "JUAN PEREZ",
                "nit": "1234567",
                "lugar_pago": "BCP",
                "detalles": [
                    {"numero_cuota": 1, "importe_cuota": 100.50}
                ]
            }
        }
    )


class PagoDataResponse(BaseModel):
    codigo_busqueda: str = Field(..., description="Código del cliente (igual al request)")
    id_txn_empresa: str = Field(..., description="ID generado por la empresa (UUID)")
    id_txn_entidad: int = Field(..., description="ID recibido desde la entidad/banco")
    razon_social: Optional[str] = Field(None, max_length=36, description="Razón social de la empresa")
    casa_matriz: Optional[str] = Field(None, max_length=15)
    direccion: Optional[str] = Field(None, max_length=33)
    telefono: Optional[str] = Field(None, max_length=20)
    ciudad_dosificacion: Optional[str] = Field(None, max_length=20)
    nit: Optional[str] = Field(None, max_length=15)
    nro_autorizacion: Optional[str] = Field(None, max_length=15)
    nro_factura: Optional[str] = Field(None, max_length=20)
    actividad_economica: Optional[str] = Field(None, max_length=22)
    hora_emision_fac: Optional[str] = Field(None, max_length=8)
    fecha_emision_fac: Optional[str] = Field(None, max_length=10)
    detalle_factura: Optional[str] = Field(None, max_length=40)
    importe_original: Optional[str] = Field(None, max_length=11)
    tipo_cambio: Optional[str] = Field(None, max_length=10)
    importe_total: Optional[str] = Field(None, max_length=13)
    literal_importe_total: Optional[str] = Field(None, max_length=69)
    codigo_control: Optional[str] = Field(None, max_length=19)
    fecha_lim_emision: Optional[str] = Field(None, max_length=10)
    cadena_qr: Optional[str] = Field(None, description="Cadena para generar el código QR fiscal")


class PagoStandardResponse(BaseModel):
    code: str = Field(..., description="Código de respuesta")
    message: str = Field(..., description="Mensaje descriptivo")
    data: Optional[PagoDataResponse] = Field(default=None, description="Datos del pago")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "code": "000",
                "message": "PROCESO CONFORME",
                "data": {
                    "codigo_busqueda": "1231231231",
                    "id_txn_empresa": "550e8400-e29b-41d4-a716-446655440000",
                    "id_txn_entidad": 123456789,
                    "razon_social": None,
                    "casa_matriz": None,
                    "direccion": None,
                    "telefono": None,
                    "ciudad_dosificacion": None,
                    "nit": None,
                    "nro_autorizacion": None,
                    "nro_factura": None,
                    "actividad_economica": None,
                    "hora_emision_fac": None,
                    "fecha_emision_fac": None,
                    "detalle_factura": None,
                    "importe_original": None,
                    "tipo_cambio": None,
                    "importe_total": None,
                    "literal_importe_total": None,
                    "codigo_control": None,
                    "fecha_lim_emision": None,
                    "cadena_qr": None
                }
            }
        }
    )