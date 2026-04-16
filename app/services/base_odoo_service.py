from typing import Any, Dict, Iterable, List, Optional, Union


class BaseOdooService:
    def __init__(self, model_name: str, client):
        self.client = client
        self.model = client.model(model_name)

    # 🔥 READ flexible
    def get(
        self,
        record_ids: Union[int, Iterable[int]],
        fields: Optional[List[str]] = None,
    ):
        if isinstance(record_ids, int):
            record_ids = [record_ids]

        return self.model.read(record_ids, fields or [])

    # CREATE
    def create(self, vals: Dict[str, Any]):
        return self.model.create(vals)

    # WRITE
    def update(
        self,
        record_ids: Union[int, Iterable[int]],
        vals: Dict[str, Any],
    ):
        if isinstance(record_ids, int):
            record_ids = [record_ids]

        return self.model.write(record_ids, vals)

    # DELETE
    def delete(self, record_ids: Union[int, Iterable[int]]):
        if isinstance(record_ids, int):
            record_ids = [record_ids]

        return self.model.unlink(record_ids)

    # SEARCH
    def search(
        self,
        domain=None,
        offset: int = 0,
        limit: Optional[int] = None,
        order: Optional[str] = None,
    ):
        return self.model.search(domain or [], offset=offset, limit=limit, order=order)

    # SEARCH + READ (🔥 importante)
    def search_read(
        self,
        domain=None,
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

        # limpia None
        options = {k: v for k, v in options.items() if v is not None}

        return self.model.search_read(domain or [], options)

    # método genérico
    def call(self, method: str, *args, **kwargs):
        return self.client.execute_kw(self.model.model, method, args=args, kwargs=kwargs)

    # magia para métodos dinámicos
    def __getattr__(self, item: str):
        def _method(*args: Any, **kwargs: Any):
            return self.client.execute_kw(self.model.model, item, args=args, kwargs=kwargs)

        return _method