import json
from typing import Any, Optional, Union

import redis.asyncio as redis

from app.core.config import settings
from app.core.logger import get_logger
from app.core.exceptions import AppException
from app.core.error_registry import ErrorRegistry

logger = get_logger(__name__)


class RedisClient:
    def __init__(self):
        self._client: Optional[redis.Redis] = None

    # =========================
    # CONNECTION
    # =========================
    async def connect(self):
        if not self._client:
            try:
                self._client = redis.Redis.from_url(
                    settings.REDIS_URL,
                    decode_responses=True,
                    socket_timeout=5,
                    socket_connect_timeout=5,
                )
                await self._client.ping()
                logger.info("Redis conectado")
            except redis.RedisError as e:
                logger.error("Error conectando a Redis", extra={"error": str(e)})
                raise AppException(ErrorRegistry.REDIS_CONNECTION_FAILED)

    async def disconnect(self):
        if self._client:
            await self._client.close()
            logger.info("Redis desconectado")

    async def get_client(self) -> redis.Redis:
        if not self._client:
            await self.connect()
        return self._client

    # =========================
    # BASIC OPERATIONS
    # =========================
    async def get(self, key: str) -> Optional[str]:
        try:
            client = await self.get_client()
            return await client.get(key)
        except redis.RedisError as e:
            logger.error("Redis GET error", extra={"key": key, "error": str(e)})
            raise AppException(ErrorRegistry.REDIS_OPERATION_FAILED)

    async def set(self, key: str, value: Union[str, int], ex: Optional[int] = None):
        try:
            client = await self.get_client()
            await client.set(key, value, ex=ex)
        except redis.RedisError as e:
            logger.error("Redis SET error", extra={"key": key, "error": str(e)})
            raise AppException(ErrorRegistry.REDIS_OPERATION_FAILED)

    async def delete(self, key: str):
        try:
            client = await self.get_client()
            await client.delete(key)
        except redis.RedisError as e:
            logger.error("Redis DELETE error", extra={"key": key, "error": str(e)})
            raise AppException(ErrorRegistry.REDIS_OPERATION_FAILED)

    # =========================
    # JSON HELPERS 🔥
    # =========================
    async def set_json(self, key: str, value: Any, ex: Optional[int] = None):
        try:
            serialized = json.dumps(value)
            await self.set(key, serialized, ex=ex)
        except Exception as e:
            logger.error("Redis SET JSON error", extra={"key": key, "error": str(e)})
            raise AppException(ErrorRegistry.REDIS_OPERATION_FAILED)

    async def get_json(self, key: str) -> Optional[Any]:
        try:
            data = await self.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.error("Redis GET JSON error", extra={"key": key, "error": str(e)})
            raise AppException(ErrorRegistry.REDIS_OPERATION_FAILED)

    # =========================
    # CACHE PATTERN 🔥
    # =========================
    async def get_or_set(
        self,
        key: str,
        callback,
        ex: int = 60,
    ):
        """
        Cache pattern:
        - intenta obtener de Redis
        - si no existe, ejecuta callback y guarda
        """
        try:
            cached = await self.get_json(key)
            if cached:
                return cached

            result = await callback()

            await self.set_json(key, result, ex=ex)

            return result

        except Exception as e:
            logger.error("Redis get_or_set error", extra={"key": key, "error": str(e)})
            raise

    # =========================
    # LOCK 🔒 (muy útil)
    # =========================
    async def acquire_lock(self, key: str, ttl: int = 5) -> bool:
        try:
            client = await self.get_client()
            return await client.set(key, "1", nx=True, ex=ttl)
        except redis.RedisError as e:
            logger.error("Redis LOCK error", extra={"key": key, "error": str(e)})
            return False

    async def release_lock(self, key: str):
        try:
            client = await self.get_client()
            await client.delete(key)
        except redis.RedisError as e:
            logger.error("Redis UNLOCK error", extra={"key": key, "error": str(e)})


# instancia global
redis_client = RedisClient()


async def get_redis() -> RedisClient:
    return redis_client