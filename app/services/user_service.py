# app/services/user_service.py

from app.core.exceptions import AppException
from app.core.logger import get_logger

from app.schemas.user import UserCreate, UserResponse
from app.core.error_registry import ErrorRegistry

logger = get_logger(__name__)


class UserService:

    def __init__(self):
        self._fake_db = []

    def create_user(self, user: UserCreate) -> UserResponse:
        logger.info("creating user", extra={"email": user.email})

        if any(u["email"] == user.email for u in self._fake_db):
            logger.warning("duplicate email attempt", extra={"email": user.email})
            raise ValueError("Email already exists")  # (puedes convertir luego a AppException)

        new_user = {
            "id": len(self._fake_db) + 1,
            "email": user.email,
            "name": user.name
        }

        self._fake_db.append(new_user)

        logger.info("user created", extra={"user_id": new_user["id"]})

        return UserResponse(**new_user)

    def get_me(self) -> UserResponse:
        logger.info("fetching current user")

        return UserResponse(id=1, email="test@mail.com", name="Otmar")

    def get_user(self, user_id: int):
        logger.info("fetching user", extra={"user_id": user_id})

        if user_id != 1:
            logger.warning("user not found", extra={"user_id": user_id})
            raise AppException(ErrorRegistry.USER_NOT_FOUND)


        return {"id": 1}