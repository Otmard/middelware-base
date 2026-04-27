from fastapi import APIRouter, Depends

from app.core.security import get_current_payload, require_scopes


router = APIRouter(prefix="/test-auth", tags=["auth-test"])


@router.get("/me")
async def me(payload=Depends(get_current_payload)):
    return payload

@router.get("/users")
async def get_users(
    payload=Depends(require_scopes(["test:test"]))
):
    return {"ok": True}