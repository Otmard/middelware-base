# app/core/middleware.py
import time
import uuid
from fastapi import Request
from app.core.logger import get_logger

logger = get_logger("http")

async def logging_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start_time = time.time()

    response = await call_next(request)

    duration = round(time.time() - start_time, 4)

    logger.info(
        "request completed",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status": response.status_code,
            "duration": duration,
        }
    )

    response.headers["X-Request-ID"] = request_id

    return response