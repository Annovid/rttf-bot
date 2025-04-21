import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

from utils.models import UserConfig
from utils.settings import settings
from utils.custom_logger import logger

from datetime import date


engine = sa.create_engine(settings.DB_URL)

Base = declarative_base()


class DBUserConfig(Base):
    __tablename__ = 'user_configs'

    id: int = sa.Column(sa.Integer, primary_key=True)
    config: dict = sa.Column(sa.JSON, nullable=False)

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




class DBTournament(Base):
    __tablename__ = 'tournaments'

    id: int = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
    tournament_date: date = sa.Column(sa.Date, nullable=False)
    info_json: str = sa.Column(sa.String, nullable=True)
    # Когда наступает next_update_dtm турнир подхватывается кроном
    # обрабатывающим обновление статусов игр
    # NULL означает, что апдейты по этому турниру больше не нужны
    next_update_dtm: int = sa.Column(sa.Integer, nullable=True)
    players: str = sa.Column(sa.String, nullable=True)

    def set_players(self, players: list[int]):
        "Переводит список интов в строку"
        players_str = ",".join([f"_{player_id}_" for player_id in players])
        self.players = players_str
    
    @classmethod
    def contains_player(cls, player_id: int):
        return cls.players.like(f"%_{player_id}_%")

    

class DBSubscription(Base):
    __tablename__ = 'subscriptions'

    user_id: int = sa.Column(
        sa.Integer, sa.ForeignKey('user_configs.id'), primary_key=True
    )
    player_id: int = sa.Column(sa.Integer, primary_key=True)

    @classmethod
    def process_subs_diff(cls, session: Session, old_config: UserConfig, new_config: UserConfig):
        """Обрабатывает изменения подписок пользователя.
        Если subscription_on меняется с False на True, добавляет все друзей из new_config.
        Если меняется с True на False, удаляет все подписки.
        В противном случае обрабатывает разницу между списками друзей.
        """
        user_id = old_config.id

        if not old_config.subscription_on and new_config.subscription_on:
            # subscription_on переключился с False на True - добавить ВСЕ друзей из new_config
            for friend_id in new_config.friend_ids:
                sub = cls(user_id=user_id, player_id=friend_id)
                if not session.query(cls).filter_by(user_id=user_id, player_id=friend_id).first():
                    sub = cls(user_id=user_id, player_id=friend_id)
                    session.add(sub)
            return
        elif old_config.subscription_on and not new_config.subscription_on:
            # subscription_on переключился с True на False - удалить все подписки для этого пользователя
            session.query(cls).filter_by(user_id=user_id).delete()
            return
        
        if not new_config.subscription_on:
            return

        # Если статус subscription_on не изменился, обрабатываем разницу между списками друзей:
        added_ids = new_config.friend_ids - old_config.friend_ids
        for added_id in added_ids:
            if not session.query(cls).filter_by(user_id=user_id, player_id=added_id).first():
                sub = cls(user_id=user_id, player_id=added_id)
                session.add(sub)
        
        removed_ids = old_config.friend_ids - new_config.friend_ids
        for removed_id in removed_ids:
            sub = session.query(cls).filter_by(user_id=user_id, player_id=removed_id).first()
            if sub:
                session.delete(sub)



class DBPlayerTournament(Base):
    __tablename__ = 'player_tournament'

    player_id: int = sa.Column(sa.Integer, primary_key=True)
    tournament_id: int = sa.Column(
        sa.Integer, sa.ForeignKey('tournaments.id'), primary_key=True
    )
    info_json: str = sa.Column(sa.String)
