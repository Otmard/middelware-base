# app/database/models.py

from datetime import datetime
from uuid import uuid4
from sqlmodel import Field, SQLModel
from typing import Optional, Any
import json


class AuditBase(SQLModel):
    pass


class Audit(AuditBase, table=True):
    __tablename__ = "audit"

    id: Optional[int] = Field(default=None, primary_key=True)
    uuid: str = Field(default_factory=lambda: str(uuid4()), index=True)
    endpoint: str = Field(index=True)
    method: str = Field(default="POST")
    request_body: Optional[str] = Field(default=None)
    response_body: Optional[str] = Field(default=None)
    status_code: int = Field(default=200)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)


class PagoRequest(AuditBase, table=True):
    __tablename__ = "pago_request"

    id: Optional[int] = Field(default=None, primary_key=True)
    audit_id: Optional[int] = Field(default=None, foreign_key="audit.id")
    id_transaccion: int = Field(index=True)
    fecha_pago: str = Field(index=True)
    codigo_busqueda: str = Field(index=True)
    monto_total: float
    nombre_factura: Optional[str] = Field(default=None)
    nit: Optional[str] = Field(default=None)
    lugar_pago: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)


class PagoDetalle(AuditBase, table=True):
    __tablename__ = "pago_detalle"

    id: Optional[int] = Field(default=None, primary_key=True)
    pago_request_id: Optional[int] = Field(default=None, foreign_key="pago_request.id")
    numero_cuota: int
    importe_cuota: float
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)


class PagoResponse(AuditBase, table=True):
    __tablename__ = "pago_response"

    id: Optional[int] = Field(default=None, primary_key=True)
    audit_id: Optional[int] = Field(default=None, foreign_key="audit.id")
    id_txn_empresa: int = Field(default=1, index=True)
    id_txn_entidad: int = Field(index=True)
    codigo_busqueda: Optional[str] = Field(default=None)
    razon_social: Optional[str] = Field(default=None)
    casa_matriz: Optional[str] = Field(default=None)
    direccion: Optional[str] = Field(default=None)
    telefono: Optional[str] = Field(default=None)
    ciudad_dosificacion: Optional[str] = Field(default=None)
    nit: Optional[str] = Field(default=None)
    nro_autorizacion: Optional[str] = Field(default=None)
    nro_factura: Optional[str] = Field(default=None)
    actividad_economica: Optional[str] = Field(default=None)
    hora_emision_fac: Optional[str] = Field(default=None)
    fecha_emision_fac: Optional[str] = Field(default=None)
    detalle_factura: Optional[str] = Field(default=None)
    importe_original: Optional[str] = Field(default=None)
    tipo_cambio: Optional[str] = Field(default=None)
    importe_total: Optional[str] = Field(default=None)
    literal_importe_total: Optional[str] = Field(default=None)
    codigo_control: Optional[str] = Field(default=None)
    fecha_lim_emision: Optional[str] = Field(default=None)
    cadena_qr: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)


class ClienteRequest(AuditBase, table=True):
    __tablename__ = "cliente_request"

    id: Optional[int] = Field(default=None, primary_key=True)
    audit_id: Optional[int] = Field(default=None, foreign_key="audit.id")
    CodServicio: str = Field(index=True)
    codigo_busqueda: str = Field(index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)


class ClienteResponse(AuditBase, table=True):
    __tablename__ = "cliente_response"

    id: Optional[int] = Field(default=None, primary_key=True)
    audit_id: Optional[int] = Field(default=None, foreign_key="audit.id")
    codigo_busqueda: Optional[str] = Field(default=None)
    codigo_servicio: Optional[str] = Field(default=None)
    importe_adeudado: Optional[str] = Field(default=None)
    importe_minimo: Optional[str] = Field(default=None)
    importe_comision: Optional[str] = Field(default=None)
    nombre_cliente: Optional[str] = Field(default=None)
    pagos: Optional[str] = Field(default=None)
    code: Optional[str] = Field(default=None)
    message: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)