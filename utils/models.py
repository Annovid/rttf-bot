import datetime
import enum
from dataclasses import dataclass, field
from typing import Any


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

    def to_dict(self) -> dict[str, Any]:
        """Конвертирует объект в словарь."""
        return {
            'id': self.id,
            'state_machine': self.state.value,
            'friend_ids': list(self.friend_ids),
        }

    @classmethod
    def from_dict(cls, state_dict: dict[str, Any]) -> 'UserConfig':
        """Инициализирует объект из словаря."""
        return UserConfig(
            id=state_dict['id'],
            state=StateMachine(state_dict['state_machine']),
            friend_ids=set(state_dict['friend_ids']),
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
        self.date_from = date_from if date_from is not None else datetime.date.today()
        self.date_to = (
            date_to if date_to else self.date_from + datetime.timedelta(days=1)
        )

    def from_ints(self, days_from: int = 0, days_to: int = 0):
        self.date_from = datetime.date.today() + datetime.timedelta(days=days_from)
        self.date_to = datetime.date.today() + datetime.timedelta(days=days_to)


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
class Tournament:
    id: int
    name: str
    registered_players: list[Player]
    refused_players: list[Player]

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
