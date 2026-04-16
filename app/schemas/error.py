# app/schemas/error.py

from pydantic import BaseModel

class ErrorResponse(BaseModel):
    code: str
    message: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "code": "USER_NOT_FOUND",
                "message": "User not found"
            }
        }
    }