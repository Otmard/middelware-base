# app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App
    APP_NAME: str = "FastAPI App"
    ENV: str = "development"
    LOG_LEVEL: str = "INFO"

    # Odoo
    ODOO_URL: str
    ODOO_DB: str
    ODOO_USERNAME: str
    ODOO_PASSWORD: str

    # Logto
    LOGTO_URL: str
    LOGTO_APP_ID: str
    LOGTO_APP_SECRET: str
    
    LOGTO_AUDIENCE: str
    # Redis
    REDIS_URL: str

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
