import enum
from dataclasses import dataclass, field
from typing import Any


class StateMachine(enum.Enum):
    MAIN = "main_state"
    ADD_FRIEND = "add_friend_state"
    DELETE_FRIEND = "delete_friend_state"
    CHANGE_CONFIG_MODE = "change_config_mode"

    def to_dict(self):
        """Сериализация ENUM в словарь."""
        return {"state": self.value}

    @classmethod
    def from_dict(cls, state_dict):
        """Десериализация из словаря обратно в ENUM."""
        return cls(state_dict["state"])


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
            id=state_dict["id"],
            state=StateMachine(state_dict["state_machine"]),
            friend_ids = set(state_dict["friend_ids"])
        )
