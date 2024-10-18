import os

from pydantic_settings import BaseSettings

ENV_PATH = os.path.join(os.getcwd(), "resources", ".env")


class Settings(BaseSettings):
    DB_URL: str = ""
    DEBUG: bool = False
    TOKEN: str = ""

    class Config:
        env_file = ENV_PATH


settings = Settings()
