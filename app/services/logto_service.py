import time
import httpx
from typing import Optional, Dict, Any


from app.core.exceptions import AppException
from app.core.logger import get_logger
from app.core.error_registry import ErrorRegistry
from app.core.config import settings

from app.schemas.logto_user_schema import (
    UserLogtoCreateSchema,
    UserLogtoUpdateSchema,
)

logger = get_logger(__name__)


class LogtoClient:
    def __init__(self):
        self.base_url = settings.LOGTO_URL
        self.api_url = f"{self.base_url}/api"
        self.app_id = settings.LOGTO_APP_ID
        self.app_secret = settings.LOGTO_APP_SECRET

        self.client = httpx.AsyncClient(timeout=10.0)

    # =========================
    # TOKEN
    # =========================
    async def _get_token(self) -> str:
        redis = await get_redis()

        token_key = "logto_access_token"
        expire_key = "logto_access_token_expire"

        now = int(time.time())

        token = await redis.get(token_key)
        expire = await redis.get(expire_key)

        if token and expire and now < int(expire):
            return token.decode() if isinstance(token, bytes) else token

        # 🔒 lock simple para evitar múltiples requests
        lock = await redis.set("logto_token_lock", "1", nx=True, ex=5)

        if not lock:
            logger.info("Esperando token existente")
            await asyncio.sleep(1)
            token = await redis.get(token_key)
            if token:
                return token.decode() if isinstance(token, bytes) else token

        logger.info("Solicitando nuevo token a Logto")

        try:
            response = await self.client.post(
                f"{self.base_url}/oidc/token",
                auth=(self.app_id, self.app_secret),
                data={
                    "grant_type": "client_credentials",
                    "scope": "all",
                    "resource": settings.LOGTO_BASE_RESOURCE,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

            response.raise_for_status()
            payload = response.json()

        except httpx.HTTPStatusError as e:
            logger.error("Error HTTP obteniendo token", extra={"status": e.response.status_code})
            raise AppException(ErrorRegistry.EXTERNAL_SERVICE_ERROR)

        except httpx.RequestError:
            logger.error("Error de conexión con Logto")
            raise AppException(ErrorRegistry.EXTERNAL_SERVICE_ERROR)

        access_token = payload.get("access_token")
        expires_in = payload.get("expires_in")

        if not access_token or not expires_in:
            logger.error("Respuesta inválida de Logto", extra={"payload": payload})
            raise AppException(ErrorRegistry.EXTERNAL_SERVICE_ERROR)

        ttl = expires_in - 30
        expire_ts = now + ttl

        await redis.set(token_key, access_token, ex=ttl)
        await redis.set(expire_key, expire_ts, ex=ttl)

        return access_token

    async def _headers(self) -> Dict[str, str]:
        token = await self._get_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    # =========================
    # USERS
    # =========================
    async def create_user(self, data: UserLogtoCreateSchema) -> Dict[str, Any]:
        logger.info("Creando usuario en Logto")

        try:
            response = await self.client.post(
                f"{self.api_url}/users",
                headers=await self._headers(),
                json=data.model_dump(exclude_none=True),
            )
            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.error("Error creando usuario", extra={"error": str(e)})
            raise AppException(ErrorRegistry.EXTERNAL_SERVICE_ERROR)

    async def update_user(self, user_id: str, data: UserLogtoUpdateSchema) -> Dict[str, Any]:
        logger.info("Actualizando usuario", extra={"user_id": user_id})

        try:
            response = await self.client.patch(
                f"{self.api_url}/users/{user_id}",
                headers=await self._headers(),
                json=data.model_dump(exclude_none=True),
            )
            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.error("Error actualizando usuario", extra={"user_id": user_id, "error": str(e)})
            raise AppException(ErrorRegistry.EXTERNAL_SERVICE_ERROR)

    async def delete_user(self, user_id: str) -> Dict[str, Any]:
        logger.warning("Eliminando usuario", extra={"user_id": user_id})

        try:
            response = await self.client.delete(
                f"{self.api_url}/users/{user_id}",
                headers=await self._headers(),
            )
            response.raise_for_status()
            return {"message": f"Usuario {user_id} eliminado"}

        except Exception as e:
            logger.error("Error eliminando usuario", extra={"user_id": user_id, "error": str(e)})
            raise AppException(ErrorRegistry.EXTERNAL_SERVICE_ERROR)

    async def update_password(self, user_id: str, password: str):
        logger.info("Actualizando contraseña", extra={"user_id": user_id})

        try:
            response = await self.client.patch(
                f"{self.api_url}/users/{user_id}/password",
                headers=await self._headers(),
                json={"password": password},
            )
            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.error("Error actualizando password", extra={"user_id": user_id, "error": str(e)})
            raise AppException(ErrorRegistry.EXTERNAL_SERVICE_ERROR)

    # =========================
    # ROLES
    # =========================
    async def set_role(self, user_id: str):
        logger.info("Asignando rol", extra={"user_id": user_id})

        try:
            response = await self.client.post(
                f"{self.api_url}/users/{user_id}/roles",
                headers=await self._headers(),
                json={"roleIds": [self.role_id]},
            )
            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.error("Error asignando rol", extra={"user_id": user_id, "error": str(e)})
            raise AppException(ErrorRegistry.EXTERNAL_SERVICE_ERROR)

    # =========================
    # ORGANIZATIONS
    # =========================
    async def add_user_to_organization(self, user_id: str, organization_id: str):
        logger.info("Agregando usuario a organización", extra={"user_id": user_id, "org": organization_id})

        try:
            headers = await self._headers()

            check = await self.client.get(
                f"{self.api_url}/users/{user_id}/organizations",
                headers=headers,
            )
            check.raise_for_status()

            for org in check.json():
                if org["id"] == organization_id:
                    return {"status": "exists"}

            response = await self.client.post(
                f"{self.api_url}/organizations/{organization_id}/users",
                headers=headers,
                json={"userIds": [user_id]},
            )
            response.raise_for_status()

            return {"status": "added"}

        except Exception as e:
            logger.error("Error agregando a organización", extra={"error": str(e)})
            raise AppException(ErrorRegistry.EXTERNAL_SERVICE_ERROR)

    # =========================
    # QUERY
    # =========================
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        logger.info("Buscando usuario por email", extra={"email": email})

        try:
            response = await self.client.get(
                f"{self.api_url}/users",
                headers=await self._headers(),
                params={
                    "search.primaryEmail": email,
                    "mode.primaryEmail": "exact",
                    "page": 1,
                    "pageSize": 1,
                },
            )
            response.raise_for_status()

            users = response.json()
            return users[0] if users else None

        except Exception as e:
            logger.error("Error buscando usuario", extra={"email": email, "error": str(e)})
            raise AppException(ErrorRegistry.EXTERNAL_SERVICE_ERROR)