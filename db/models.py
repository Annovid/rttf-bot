import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

from utils.models import UserConfig
from utils.settings import settings

from datetime import date


engine = sa.create_engine(settings.DB_URL)

Base = declarative_base()


class DBUserConfig(Base):
    __tablename__ = 'user_configs'

    id: int = sa.Column(sa.Integer, primary_key=True)
    config: dict = sa.Column(sa.JSON)

    @classmethod
    def get_all(cls, session: Session) -> list[UserConfig]:
        """Возвращает список всех конфигураций пользователей."""
        db_res: list['DBUserConfig'] = session.query(cls).all()  # noqa
        return [UserConfig.from_dict(db_config.config) for db_config in db_res]

    @classmethod
    def get_by_id(cls, session: Session, user_id: int) -> 'DBUserConfig | None':
        """Возвращает объект DBUserConfig по ID, если он существует."""
        return session.query(cls).filter_by(id=user_id).first()

    @classmethod
    def save_config(cls, user_config: UserConfig, session: Session) -> None:
        """Сохраняет или обновляет конфигурацию пользователя в базе данных."""
        # Попытка получить существующую конфигурацию DBUserConfig
        db_user_config = cls.get_by_id(session=session, user_id=user_config.id)

        if db_user_config:
            # Если конфигурация существует, обновляем поле config
            db_user_config.config = user_config.to_dict()
        else:
            # Если конфигурации нет, создаем новую запись DBUserConfig
            db_user_config = DBUserConfig(
                id=user_config.id, config=user_config.to_dict()
            )
            session.add(db_user_config)

        session.commit()


class Player(Base):
    __tablename__ = 'players'

    id: int = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
    name: str = sa.Column(sa.String, default='')


class Tournament(Base):
    __tablename__ = 'tournaments'

    id: int = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
    tournament_date: date = sa.Column(sa.Date)
    info_json: str = sa.Column(sa.String, nullable=True)
    # Когда наступает next_update_dtm турнир подхватывается кроном
    # обрабатывающим обновление статусов игр
    # NULL означает, что апдейты по этому турниру больше не нужны
    next_update_dtm: int = sa.Column(sa.Integer, nullable=True)
    

class Subscription(Base):
    __tablename__ = 'subscriptions'

    user_id: int = sa.Column(
        sa.Integer, sa.ForeignKey('user_configs.id'), primary_key=True
    )
    player_id: int = sa.Column(
        sa.Integer, sa.ForeignKey('players.id'), primary_key=True
    )


class PlayerTournament(Base):
    __tablename__ = 'player_tournament'

    player_id: int = sa.Column(
        sa.Integer, sa.ForeignKey('players.id'), primary_key=True
    )
    tournament_id: int = sa.Column(
        sa.Integer, sa.ForeignKey('tournaments.id'), primary_key=True
    )
    results_json: str = sa.Column(sa.String)
