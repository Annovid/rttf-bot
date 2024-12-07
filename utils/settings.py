import os

from pydantic_settings import BaseSettings

ENV_PATH = os.path.join(os.getcwd(), 'resources', '.env')


class Settings(BaseSettings):
    DB_URL: str = 'postgresql://user:pass@localhost:5432/rttf_bot'
    DEVELOPER_ID: int = 491372273
    SENTRY_DSN: str | None = None
    DEBUG: bool = False
    TOKEN: str = ''
    ADMIN_PASSWORD: str | None = None
    MAX_WORKERS: int = 5

    class Config:
        env_file = ENV_PATH


settings = Settings()
