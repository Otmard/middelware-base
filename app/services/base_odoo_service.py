from typing import Any, Dict, Iterable, List, Optional, Union

from app.core.odoo import OdooJsonRpcClient


class BaseOdooService:
    def __init__(self, model_name: str, client: OdooJsonRpcClient):
        self.client = client
        self.model_name = model_name
        self._model = client.model(model_name)

    def get(
        self,
        record_ids: Union[int, Iterable[int]],
        fields: Optional[List[str]] = None,
    ):
        if isinstance(record_ids, int):
            record_ids = [record_ids]
        return self._model.read(record_ids, fields or [])

    def create(self, vals: Dict[str, Any]):
        return self._model.create(vals)

    def update(
        self,
        record_ids: Union[int, Iterable[int]],
        vals: Dict[str, Any],
    ):
        if isinstance(record_ids, int):
            record_ids = [record_ids]
        return self._model.write(record_ids, vals)

    def delete(self, record_ids: Union[int, Iterable[int]]):
        if isinstance(record_ids, int):
            record_ids = [record_ids]
        return self._model.unlink(record_ids)

    def search(
        self,
        domain: Optional[List[Any]] = None,
        offset: int = 0,
        limit: Optional[int] = None,
        order: Optional[str] = None,
    ):
        return self._model.search(domain or [], offset=offset, limit=limit, order=order)

    def search_read(
        self,
        domain: Optional[List[Any]] = None,
        fields: Optional[List[str]] = None,
        limit: Optional[int] = None,
        offset: int = 0,
        order: Optional[str] = None,
    ):
        options = {
            "fields": fields or [],
            "limit": limit,
            "offset": offset,
            "order": order,
        }
        options = {k: v for k, v in options.items() if v is not None}
        return self._model.search_read(domain or [], options)

    def call(self, method: str, *args: Any, **kwargs: Any) -> Any:
        return self.client.execute_kw(self.model_name, method, args=args, kwargs=kwargs)

    def __getattr__(self, item: str):
        def _method(*args: Any, **kwargs: Any):
            return self.client.execute_kw(self.model_name, item, args=args, kwargs=kwargs)
        return _method