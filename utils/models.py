import datetime
import enum
from dataclasses import dataclass, field
from typing import Any

from utils.custom_logger import logger
import json


class StateMachine(enum.Enum):
    MAIN = 'main_state'
    ADD_FRIEND = 'add_friend_state'
    DELETE_FRIEND = 'delete_friend_state'
    CHANGE_CONFIG_MODE = 'change_config_mode'
    ADMIN = 'admin_state'

    def to_dict(self):
        """Сериализация ENUM в словарь."""
        return {'state': self.value}

    @classmethod
    def from_dict(cls, state_dict):
        """Десериализация из словаря обратно в ENUM."""
        return cls(state_dict['state'])


@dataclass
class UserConfig:
    id: int
    state: StateMachine = StateMachine.MAIN
    friend_ids: set[int] = field(default_factory=set)
    username: str | None = ""
    full_name: str | None = ""

    def to_dict(self) -> dict[str, Any]:
        """Конвертирует объект в словарь."""
        return {
            'id': self.id,
            'state_machine': self.state.value,
            'friend_ids': list(self.friend_ids),
            'username': self.username,
            'full_name': self.full_name,
        }

    @classmethod
    def from_dict(cls, user_config_dict: dict[str, Any]) -> 'UserConfig':
        """Инициализирует объект из словаря."""
        return UserConfig(
            id=user_config_dict['id'],
            state=StateMachine(user_config_dict['state_machine']),
            friend_ids=set(user_config_dict['friend_ids']),
            username=user_config_dict.get('username', ''),
            full_name=user_config_dict.get('full_name', ''),
        )


@dataclass
class DateRange:
    date_from: datetime.date
    date_to: datetime.date

    def __init__(
        self,
        date_from: datetime.date | None = None,
        date_to: datetime.date | None = None,
    ):
        date_today = datetime.date.today()
        logger.info(f"Current date (today): {date_today}")
        self.date_from = date_from if date_from is not None else date_today
        self.date_to = (
            date_to if date_to else self.date_from + datetime.timedelta(days=1)
        )

    @classmethod
    def from_ints(cls, days_from: int = 0, days_to: int = 0):
        date_from = datetime.date.today() + datetime.timedelta(days=days_from)
        date_to = datetime.date.today() + datetime.timedelta(days=days_to)
        return DateRange(
            date_from=date_from,
            date_to=date_to,
        )


@dataclass
class Player:
    id: int
    name: str
    nickname: str | None = None
    rating: int | None = None
    city: str | None = None
    hand: str | None = None

    def __repr__(self):
        return (
            f'Player('
            f'id={self.id}, '
            f'name={self.name}, '
            f'nickname={self.nickname}, '
            f'rating={self.rating}, '
            f'city={self.city}, '
            f'hand={self.hand}'
            f')'
        )

    def __post_init__(self):
        if not isinstance(self.id, int):
            raise TypeError(
                f'Invalid type for id: expected int, got {type(self.id).__name__}'
            )

    def __str__(self):
        return self.__repr__()

    def to_md(self):
        md_representation = [
            f'*ID*: [{self.id}](https://m.rttf.ru/players/{self.id})',
            f'*Name*: {self.name}',
            f'*Nickname*: {self.nickname}' if self.nickname else '',
            f'*Rating*: {self.rating}' if self.rating is not None else '',
            f'*City*: {self.city}' if self.city else '',
            f'*Hand*: {self.hand}' if self.hand else '',
        ]
        # Join non-empty strings with new lines
        return '\n'.join(filter(bool, md_representation))

    def to_md_one_str(self) -> str:
        return f'[{self.id}](https://m.rttf.ru/players/{self.id}): *{self.name}*'

    def to_md2(self):
        md_representation = [
            f'*ID*: /{self.id}',
            f'*Name*: [{self.name}](https://m.rttf.ru/players/{self.id})',
            f'*Nickname*: {self.nickname}' if self.nickname else '',
            f'*Rating*: {self.rating}' if self.rating is not None else '',
            f'*City*: {self.city}' if self.city else '',
            f'*Hand*: {self.hand}' if self.hand else '',
        ]
        # Join non-empty strings with new lines
        return '\n'.join(filter(bool, md_representation))

@dataclass
class PlayerResult:
    player_id: int
    name: str
    rating_before: float
    rating_delta: float
    rating_after: float
    games_won: int
    games_lost: int

    def to_md_one_str(self) -> str:
        return (
            f'[{self.player_id}](https://m.rttf.ru/players/{self.player_id}): *{self.name}*'
            f' rating:{self.rating_before:.0f} delta:{self.rating_delta} won:{self.games_won} lost:{self.games_lost}')

@dataclass
class Tournament:
    id: int
    name: str
    is_completed: bool = False
    registered_players: list[Player] = field(default_factory=list)
    refused_players: list[Player] = field(default_factory=list)
    player_results: list[PlayerResult] = field(default_factory=list)

    def __post_init__(self):
        if not isinstance(self.id, int):
            raise TypeError(
                f'Invalid type for id: expected int, got {type(self.id).__name__}'
            )

    def __repr__(self):
        return f'Tournament(' f'id={self.id}, ' f'name={self.name}' f')'

    def to_md(self):
        registered_players_representation = (
            '\n'.join(map(Player.to_md_one_str, self.registered_players))  # noqa
        )
        md_representation = [
            f'*ID*: [{self.id}](https://m.rttf.ru/players/{self.id})',
            f'*Name*: {self.name}',
            f'*Registered players*:\n' f'{registered_players_representation}',
        ]
        # Join non-empty strings with new lines
        return '\n'.join(filter(bool, md_representation))

    def to_md_one_str(self) -> str:
        return f'[{self.id}](https://m.rttf.ru/tournaments/{self.id}): *{self.name}*'

    def to_md_player_results(self) -> str:
        res = self.to_md_one_str()
        if not self.player_results: 
            return res
        res += '\n'
        def pr_to_str(pr: PlayerResult):
            return f"{pr:id}"
        res += '\n'.join([pr.to_md_one_str() for pr in self.player_results])
        return res


@dataclass
class PlayerTournamentInfo:
    player_id: int
    tournament_id: int
    status: str
    player_name: str = ""
    tournament_name: str = ""
    rating_before: float = ""
    rating_delta: float = ""
    rating_after: float = ""
    games_won: int = 0
    games_lost: int = 0

    def serialize(self) -> str:
        return json.dumps(self.__dict__, sort_keys=True)

    @classmethod
    def deserialize(cls, data: str) -> "PlayerTournamentInfo":
        return cls(**json.loads(data))
