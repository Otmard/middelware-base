from typing import Dict, Any

import jwt
from jwt import PyJWKClient

from app.core.config import settings
from app.core.logger import get_logger
from app.core.exceptions import AppException
from app.core.error_registry import ErrorRegistry

logger = get_logger(__name__)

# =========================
# CONFIG
# =========================
LOGTO_URL = settings.LOGTO_URL
JWKS_URI = f"{LOGTO_URL}/oidc/jwks"
ISSUER = f"{LOGTO_URL}/oidc"

jwks_client = PyJWKClient(JWKS_URI)

ALLOWED_AUDIENCES = [
    "https://test.api-fluxnet.maplenet.com.bo",
    "https://internal.api-fluxnet.maplenet.com.bo",
]
# =========================
# VALIDATE JWT
# =========================
def validate_jwt(token: str) -> Dict[str, Any]:
    try:
        signing_key = jwks_client.get_signing_key_from_jwt(token)

        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["ES384"],
            issuer=ISSUER,
            options={"verify_aud": False},  # 👈 desactivamos validación automática
        )

        aud = payload.get("aud")

        # 🔥 validación manual (soporta string o list)
        if isinstance(aud, str):
            aud = [aud]

        if not any(a in ALLOWED_AUDIENCES for a in aud):
            logger.warning("Audience no permitido", extra={"aud": aud})
            raise AppException(ErrorRegistry.UNAUTHORIZED)

        logger.info(
            "JWT validado correctamente",
            extra={
                "sub": payload.get("sub"),
                "client_id": payload.get("client_id"),
                "aud": aud,
            },
        )

        return payload

    except jwt.ExpiredSignatureError:
        raise AppException(ErrorRegistry.TOKEN_EXPIRED)

    except jwt.InvalidIssuerError:
        raise AppException(ErrorRegistry.UNAUTHORIZED)

    except jwt.InvalidTokenError as e:
        logger.error("Token inválido", extra={"error": str(e)})
        raise AppException(ErrorRegistry.UNAUTHORIZED)

    except Exception as e:
        logger.error("Error validando JWT", extra={"error": str(e)})
        raise AppException(ErrorRegistry.INTERNAL_ERROR)