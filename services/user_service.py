import sqlalchemy as sa

from db.models import DBUserConfig
from db.session_factory import open_session
from utils.models import UserConfig


class UserService:
    """Сервис для работы с пользовательскими конфигурациями напрямую через Postgres."""
    def __init__(self):
        pass

    @staticmethod
    def get_user_config(user_id: int) -> UserConfig:
        """Получает конфигурацию пользователя из базы данных."""
        with open_session() as session:
            db_user_config: DBUserConfig | None = (
                session.query(DBUserConfig).
                filter(DBUserConfig.id == user_id)
                .first()
            )
            if db_user_config is None:
                new_user_config = UserService._create_default_user_config(user_id, session)
                UserService.save_user_config(new_user_config)
                return new_user_config
            return UserConfig.from_dict(db_user_config.config)

    @staticmethod
    def save_user_config(user_config: UserConfig) -> None:
        """Сохраняет конфигурацию пользователя в базу данных."""
        with open_session() as session:
            db_user_config: DBUserConfig = DBUserConfig(
                id=user_config.id, config=user_config.to_dict()
            )
            session.merge(db_user_config)
            session.commit()

    @staticmethod
    def _create_default_user_config(user_id: int, session: sa.orm.Session) -> UserConfig:
        """Создает и сохраняет новую конфигурацию пользователя с настройками по умолчанию."""
        db_user_config = UserConfig(id=user_id)
        session.add(db_user_config)
        session.commit()
        return db_user_config

    @staticmethod
    def delete_user_config(user_id: int) -> None:
        """Удаляет конфигурацию пользователя из базы данных."""
        with open_session() as session:
            session.query(DBUserConfig).filter(DBUserConfig.id == user_id).delete()
            session.commit()
