from typing import Dict, Any, List

from fastapi import Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.jwt import validate_jwt
from app.core.logger import get_logger
from app.core.exceptions import AppException
from app.core.error_registry import ErrorRegistry

logger = get_logger(__name__)

security = HTTPBearer()


# =========================
# BASE AUTH
# =========================
def get_current_payload(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> Dict[str, Any]:

    token = credentials.credentials
    payload = validate_jwt(token)

    return payload


# =========================
# SCOPES AUTH 🔥
# =========================
def require_scopes(required_scopes: List[str]):
    def dependency(
        payload: Dict[str, Any] = Depends(get_current_payload),
    ):

        token_scopes = payload.get("scope", "").split()

        missing = [s for s in required_scopes if s not in token_scopes]

        if missing:
            logger.warning(
                "Scopes insuficientes",
                extra={
                    "required": required_scopes,
                    "token_scopes": token_scopes,
                },
            )
            raise AppException(ErrorRegistry.UNAUTHORIZED)

        return payload

    return dependency   