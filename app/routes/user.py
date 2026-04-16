# app/api/routes/user.py

from fastapi import APIRouter, Depends, status
from app.core.error_registry import  ErrorRegistry, build_error_responses
from app.schemas.user import UserCreate, UserResponse
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


def get_user_service():
    return UserService()


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, service: UserService = Depends(get_user_service)):
    # ya NO manejas try/except aquí
    return service.create_user(payload)


@router.get(
    "/me",
    response_model=UserResponse,
    responses=build_error_responses(
        ErrorRegistry.USER_NOT_FOUND, ErrorRegistry.UNAUTHORIZED
    ),
)
def get_me(service: UserService = Depends(get_user_service)):
    return service.get_me()


@router.get("/{user_id}")
def get_user(user_id: int, service: UserService = Depends(get_user_service)):
    return service.get_user(user_id)
