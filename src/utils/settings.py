import os
from pydantic import Field
from pydantic_settings import BaseSettings

ENV_PATH = os.path.join(os.getcwd(), '.env')


class Settings(BaseSettings):
    ENVIRONMENT: str = Field(
        default='UNDEFINED',
        description="Тип окружения: LOCAL, STAGE, PROD и т.д."
    )

    SERVICE_NAME: str = Field(
        default='rttf_bot_app',
        description="Название сервиса: rttf_bot_app, rttf_bot_cron"
    )

    DB_URL: str = Field(
        default='postgresql://user:pass@localhost:5432/rttf_bot',
        description="Строка подключения к базе данных Postgres"
    )

    SENTRY_DSN: str | None = Field(
        default=None,
        description="DSN для интеграции с Sentry (можно оставить пустым)"
    )

    DEBUG: bool = Field(
        default=False,
        description="Флаг отладки. True включает режим отладки"
    )

    TOKEN: str = Field(
        default='',
        description="Токен бота или сервиса"
    )

    MAX_WORKERS: int = Field(
        default=5,
        description="Максимальное количество потоков или воркеров"
    )

    USE_LOKI: bool = Field(
        default=False,
        description="Флаг: включить ли отправку логов в Loki"
    )

    LOKI_URL: str = Field(
        default="localhost:3100",
        description="Адрес сервера Loki (без схемы http://)"
    )

    class Config:
        extra = "ignore"
        env_file = ENV_PATH


settings = Settings()
