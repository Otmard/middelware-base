# app/database/audit_repository.py

import json
from uuid import uuid4
from datetime import datetime
from sqlmodel import select
from app.database.models import Audit, PagoRequest, PagoDetalle, PagoResponse, ClienteRequest, ClienteResponse
from app.database.database import async_session_maker


class AuditRepository:
    @staticmethod
    async def create_audit(endpoint: str, method: str, request_body: dict, response_body: dict, status_code: int) -> Audit:
        import re
        def convert_value(v):
            from decimal import Decimal
            if isinstance(v, Decimal):
                return str(v)
            if isinstance(v, (list, tuple)):
                return [convert_value(i) for i in v]
            if isinstance(v, dict):
                return {kk: convert_value(vv) for kk, vv in v.items()}
            return v
        
        request_body_clean = {k: convert_value(v) for k, v in request_body.items()} if request_body else {}
        response_body_clean = {k: convert_value(v) for k, v in response_body.items()} if response_body else {}
        
        async with async_session_maker() as session:
            audit = Audit(
                uuid=str(uuid4()),
                endpoint=endpoint,
                method=method,
                request_body=json.dumps(request_body_clean) if request_body_clean else None,
                response_body=json.dumps(response_body_clean) if response_body_clean else None,
                status_code=status_code,
            )
            session.add(audit)
            await session.commit()
            await session.refresh(audit)
            return audit

    @staticmethod
    async def create_pago_request(audit_id: int, data: dict) -> PagoRequest:
        async with async_session_maker() as session:
            pago_req = PagoRequest(
                audit_id=audit_id,
                id_transaccion=data.get("id_transaccion"),
                fecha_pago=data.get("fecha_pago"),
                codigo_busqueda=data.get("codigo_busqueda"),
                monto_total=data.get("monto_total"),
                nombre_factura=data.get("nombre_factura"),
                nit=data.get("nit"),
                lugar_pago=data.get("lugar_pago"),
            )
            session.add(pago_req)
            await session.commit()
            await session.refresh(pago_req)
            
            detalles = data.get("detalles", [])
            for det in detalles:
                detalle = PagoDetalle(
                    pago_request_id=pago_req.id,
                    numero_cuota=det.get("numero_cuota"),
                    importe_cuota=det.get("importe_cuota"),
                )
                session.add(detalle)
            
            if detalles:
                await session.commit()
            
            return pago_req

    @staticmethod
    async def create_pago_response(audit_id: int, data: dict, id_txn_empresa: int) -> PagoResponse:
        async with async_session_maker() as session:
            pago_resp = PagoResponse(
                audit_id=audit_id,
                id_txn_empresa=id_txn_empresa,
                id_txn_entidad=data.get("id_txn_entidad"),
                codigo_busqueda=data.get("codigo_busqueda"),
                razon_social=data.get("razon_social"),
                casa_matriz=data.get("casa_matriz"),
                direccion=data.get("direccion"),
                telefono=data.get("telefono"),
                ciudad_dosificacion=data.get("ciudad_dosificacion"),
                nit=data.get("nit"),
                nro_autorizacion=data.get("nro_autorizacion"),
                nro_factura=data.get("nro_factura"),
                actividad_economica=data.get("actividad_economica"),
                hora_emision_fac=data.get("hora_emision_fac"),
                fecha_emision_fac=data.get("fecha_emision_fac"),
                detalle_factura=data.get("detalle_factura"),
                importe_original=data.get("importe_original"),
                tipo_cambio=data.get("tipo_cambio"),
                importe_total=data.get("importe_total"),
                literal_importe_total=data.get("literal_importe_total"),
                codigo_control=data.get("codigo_control"),
                fecha_lim_emision=data.get("fecha_lim_emision"),
                cadena_qr=data.get("cadena_qr"),
            )
            session.add(pago_resp)
            await session.commit()
            await session.refresh(pago_resp)
            return pago_resp

    @staticmethod
    async def create_cliente_request(audit_id: int, data: dict) -> ClienteRequest:
        async with async_session_maker() as session:
            cliente_req = ClienteRequest(
                audit_id=audit_id,
                CodServicio=data.get("CodServicio"),
                codigo_busqueda=data.get("CodigoBusqueda"),
            )
            session.add(cliente_req)
            await session.commit()
            await session.refresh(cliente_req)
            return cliente_req

    @staticmethod
    async def create_cliente_response(audit_id: int, data: dict) -> ClienteResponse:
        import re
        def convert_value(v):
            from decimal import Decimal
            if isinstance(v, Decimal):
                return str(v)
            if isinstance(v, (list, tuple)):
                return [convert_value(i) for i in v]
            if isinstance(v, dict):
                return {kk: convert_value(vv) for kk, vv in v.items()}
            return v
        
        async with async_session_maker() as session:
            cliente_resp = ClienteResponse(
                audit_id=audit_id,
                codigo_busqueda=str(data.get("codigoBusqueda")) if data.get("codigoBusqueda") else None,
                codigo_servicio=str(data.get("codigoServicio")) if data.get("codigoServicio") else None,
                importe_adeudado=str(data.get("importeAdeudado")) if data.get("importeAdeudado") else None,
                importe_minimo=str(data.get("importeMinimo")) if data.get("importeMinimo") else None,
                importe_comision=str(data.get("importeComision")) if data.get("importeComision") else None,
                nombre_cliente=str(data.get("nombreCliente")) if data.get("nombreCliente") else None,
                pagos=json.dumps(convert_value(data.get("pagos"))) if data.get("pagos") else None,
            )
            session.add(cliente_resp)
            await session.commit()
            await session.refresh(cliente_resp)
            return cliente_resp

    @staticmethod
    async def get_next_pago_id() -> int:
        async with async_session_maker() as session:
            result = await session.execute(
                select(PagoResponse).order_by(PagoResponse.id_txn_empresa.desc())
            )
            last = result.first()
            return (last[0].id_txn_empresa + 1) if last else 1