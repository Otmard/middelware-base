# app/core/exceptions.py

from app.core.error_registry import ErrorDetail

class AppException(Exception):
    def __init__(self, error: ErrorDetail):
        self.error = error
        super().__init__(error.message)