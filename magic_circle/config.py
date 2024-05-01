import os
from pathlib import Path

from pydantic_settings import BaseSettings

APP_ENV = os.environ.get("APP_ENV", "dev")
APP_NAME = os.environ.get("APP_NAME", f"magic-circle-{APP_ENV}")


class Config(BaseSettings):
    ############################################################################
    # APP
    APP_ENV: str = APP_ENV
    APP_NAME: str = APP_NAME
    APP_API_KEY: str = "admin"

    APP_DEBUG: bool = True
    APP_LOG_LEVEL: str = "INFO"
    APP_LOGGING_IGNORE: list[str] = [
        "asyncio",
        "aiosqlite",
        "httpx",
        "urllib3",
    ]
    APP_WORKER: int = 4

    APP_CACHE_PATH: str = "cache"

    ############################################################################
    # SERVICES
    DB_URL: str = "mysql+asyncmy://root:root@127.0.0.1:3306/dbname"
    DB_ENGINE_CONFIG: dict = {
        "echo": False,
        "future": True,
        "pool_recycle": 7200,
        "pool_reset_on_return": None,
    }
    DB_SESSION_CONFIG: dict = {
        "expire_on_commit": False,
    }
    REDIS_URL: str = "redis://127.0.0.1:6379"
    CELERY_WORKER: int = 4

    ############################################################################
    # FASTAPI
    FAPI_DOCS_ENABLE: bool = True
    FAPI_CORS_ENABLE: bool = True
    FAPI_CORS_ALLOW_CREDENTIALS: bool = True
    FAPI_CORS_ALLOW_ORIGINS: list[str] = ["*"]
    FAPI_CORS_ALLOW_METHODS: list[str] = ["*"]
    FAPI_CORS_ALLOW_HEADERS: list[str] = ["*"]

    def init(self):
        Path(self.APP_CACHE_PATH).mkdir(parents=True, exist_ok=True)


config = Config()
config.init()
