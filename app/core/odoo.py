import itertools
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from app.core.config import settings

# Asumo que tienes un módulo settings con ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD
# from myproject import settings


class OdooJSONRPCError(Exception):
    """Excepción custom para errores de JSON-RPC de Odoo."""
    pass

class OdooJsonRpcClient:
    """
    Cliente JSON-RPC para Odoo.

    Ejemplo:
        client = OdooJsonRpcClient(
            url=settings.ODOO_URL,
            db=settings.ODOO_DB,
            username=settings.ODOO_USERNAME,
            password=settings.ODOO_PASSWORD,
        )
        client.authenticate()
        partners = client.model("res.partner").search_read([[["is_company", "=", True]]], {"fields": ["id","name"], "limit": 5})
    """

    def __init__(
        self,
        url: str,
        db: str,
        username: str,
        password: str,
        timeout: float = 10.0,
        max_retries: int = 3,
        backoff_factor: float = 0.3,
    ) -> None:
        self.base_url = url.rstrip("/") + "/jsonrpc"
        self.db = db
        self.username = username
        self.password = password
        self.timeout = timeout

        self._id_counter = itertools.count(1)
        self.uid: Optional[int] = None

        # Session con reintentos
        self.session = requests.Session()
        retries = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=(500, 502, 503, 504),
            allowed_methods=frozenset(["POST", "GET", "PUT", "DELETE", "HEAD"]),
        )
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _rpc(self, service: str, method: str, *args: Any) -> Any:
        """
        Llamada JSON-RPC genérica a Odoo.
        service: "common" | "object" | etc.
        method: nombre del método del servicio
        args: argumentos posicionales para el método
        """
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {"service": service, "method": method, "args": list(args)},
            "id": next(self._id_counter),
        }

        try:
            resp = self.session.post(self.base_url, json=payload, timeout=self.timeout)
            resp.raise_for_status()
        except requests.RequestException as e:
            raise OdooJSONRPCError(f"Error HTTP al llamar JSON-RPC: {e}") from e

        data = resp.json()

        if "error" in data:
            err = data["error"]

            # Extraer lo más útil
            code = err.get("code")
            message = err.get("message")
            data_err = err.get("data", {})

            name = data_err.get("name")
            fault_code = data_err.get("fault_code")
            debug = data_err.get("debug")

            # Armar mensaje detallado
            details = f"Odoo JSON-RPC Error {code}: {message}"
            if name:
                details += f"\nName: {name}"
            if fault_code:
                details += f"\nFault Code: {fault_code}"
            if debug:
                details += f"\nDebug:\n{debug}"

            raise OdooJSONRPCError(details)

        return data.get("result")

    def authenticate(self) -> int:
        """Autentica y guarda uid en self.uid. Devuelve uid."""
        uid = self._rpc(
            "common", "authenticate", self.db, self.username, self.password, {}
        )
        if not uid:
            raise OdooJSONRPCError("Autenticación fallida en Odoo (uid falsy).")
        self.uid = uid
        return uid

    def execute_kw(
        self,
        model: str,
        method: str,
        args: Optional[Union[List[Any], Tuple[Any, ...]]] = None,
        kwargs: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Ejecuta object.execute_kw en Odoo via JSON-RPC.
        - model: nombre del modelo (ej. 'res.partner')
        - method: método del modelo (ej. 'search_read', 'create')
        - args: lista/tupla de argumentos posicionales para el método
        - kwargs: kwargs dict que se pasan al execute_kw (último parámetro)
        """
        if self.uid is None:
            # Intentar autenticar implícitamente si no está autenticado
            self.authenticate()

        args = list(args or [])
        kwargs = kwargs or {}
        return self._rpc(
            "object",
            "execute_kw",
            self.db,
            self.uid,
            self.password,
            model,
            method,
            args,
            kwargs,
        )

    def call(self, service: str, method: str, *args: Any) -> Any:
        """Llamada general a otros servicios si lo necesitas."""
        return self._rpc(service, method, *args)

    def model(self, model_name: str) -> "ModelProxy":
        """Devuelve un proxy para el modelo indicado (p. ej. res.partner)."""
        return ModelProxy(self, model_name)


class ModelProxy:
    """
    Proxy para un modelo Odoo, delega en client.execute_kw.
    Permite llamadas directas como client.model('res.partner').search_read(...)
    """

    def __init__(self, client: OdooJsonRpcClient, model_name: str) -> None:
        self.client = client
        self.model = model_name

    def execute(self, method: str, *args: Any, **kwargs: Any) -> Any:
        return self.client.execute_kw(self.model, method, args=args, kwargs=kwargs)

    # Métodos comunes
    def search(
        self,
        domain: Optional[List[Any]] = None,
        offset: int = 0,
        limit: Optional[int] = None,
        order: Optional[str] = None,
    ) -> List[int]:
        domain = domain or []
        params = {"offset": offset}
        if limit is not None:
            params["limit"] = limit
        if order:
            params["order"] = order
        return self.client.execute_kw(
            self.model, "search", args=(domain,), kwargs=params
        )

    def search_read(
        self,
        domain: Optional[List[Any]] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        domain = domain or []
        options = options or {}
        return self.client.execute_kw(
            self.model, "search_read", args=(domain,), kwargs=options
        )

    def read(
        self, ids: Iterable[int], fields: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        return self.client.execute_kw(
            self.model, "read", args=(list(ids), fields or []), kwargs={}
        )

    def create(self, vals: Dict[str, Any]) -> int:
        return self.client.execute_kw(self.model, "create", [vals], {})

    def write(self, ids: Iterable[int], vals: Dict[str, Any]) -> bool:
        return self.client.execute_kw(
            self.model, "write", args=(list(ids), vals), kwargs={}
        )

    def unlink(self, ids: Iterable[int]) -> bool:
        return self.client.execute_kw(
            self.model, "unlink", args=(list(ids),), kwargs={}
        )

    # Permite llamar cualquier método del modelo
    def __getattr__(self, item: str):
        def _method(*args: Any, **kwargs: Any):
            return self.client.execute_kw(self.model, item, args=args, kwargs=kwargs)

        return _method


# --- Ejemplo de adaptación de tu función existente ---
def get_odoo_connection_json() -> OdooJsonRpcClient:
    """
    Fabrica un cliente JSON-RPC autenticado listo para usar.
    Mantiene la compatibilidad funcional con la idea original de get_odoo_connection.
    """
    client = OdooJsonRpcClient(
        url=settings.ODOO_URL,
        db=settings.ODOO_DB,
        username=settings.ODOO_USERNAME,
        password=settings.ODOO_PASSWORD,
    )
    client.authenticate()
    return client


def get_odoo_connection_json_user_id(
    id: Optional[str] = None,
) -> OdooJsonRpcClient:
    usuarios = {
        "26bg43sshtze": {
            "username": "aillanes@maplenet.com.bo",
            "password": "k}'H^Wi3g+96]%*",
        },
        "1079": {
            "username": "steran@maplenet.com.bo",
            "password": "123qweASD",
        },
        "1491": {
            "username": "eovando@maplenet.com.bo",
            "password": "123qweASD",
        },
    }

    if id and id in usuarios:
        username = usuarios[id]["username"]
        password = usuarios[id]["password"]
    else:
        username = settings.ODOO_USERNAME
        password = settings.ODOO_PASSWORD

    client = OdooJsonRpcClient(
        url=settings.ODOO_URL,
        db=settings.ODOO_DB,
        username=username,
        password=password,
    )

    client.authenticate()
    return client


# --- Ejemplo de función equivalente a execute_odoo_method pero usando JSON-RPC ---
def execute_odoo_method_json(
    client: OdooJsonRpcClient,
    model: str,
    method: str,
    args: Optional[Union[List[Any], Tuple[Any, ...]]] = None,
    kwargs: Optional[Dict[str, Any]] = None,
):
    """
    Ejecuta un método en Odoo usando JSON-RPC (compatibilidad con execute_odoo_method previa).
    """
    return client.execute_kw(model, args=args or [], kwargs=kwargs or {})


# --- Ejemplo de uso ---
# if __name__ == "__main__":
# client = get_odoo_connection_json()  # descomenta y usa settings
# partners = client.model("res.partner").search_read([["is_company", "=", True]], {"fields": ["id", "name"], "limit": 5})
# print(partners)
# pass
