# app/schemas/response.py

from typing import Any, Optional, Dict
from pydantic import BaseModel, Field


class StandardResponse(BaseModel):
    code: str = Field(..., description="Código de respuesta")
    message: str = Field(..., description="Mensaje descriptivo")
    data: Optional[Any] = Field(default=None, description="Datos de respuesta")
