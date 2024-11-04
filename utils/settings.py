import os

from pydantic_settings import BaseSettings

ENV_PATH = os.path.join(os.getcwd(), "resources", ".env")


class Settings(BaseSettings):
    DB_URL: str = "postgresql://user:pass@localhost:5432/rttf_bot"
    DEVELOPER_ID: int = 491372273
    DEBUG: bool = False
    TOKEN: str = ""
    ADMIN_PASSWORD: str | None = None

    class Config:
        env_file = ENV_PATH


settings = Settings()
