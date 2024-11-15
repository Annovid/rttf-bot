import contextlib
from collections import defaultdict
from copy import deepcopy

import telebot

from db.models import DBUserConfig
from db.session_factory import open_session
from utils.models import UserConfig
from utils.settings import settings


class BotContext:
    def __init__(self):
        self.bot: telebot.TeleBot = telebot.TeleBot(
            settings.TOKEN,
            parse_mode="Markdown",
            disable_web_page_preview=True,
        )
        self.__user_config_matching: dict[int, UserConfig] = defaultdict(
            UserConfig
        )

    def load_user_config_matching(self) -> None:
        with open_session() as session:
            user_configs = DBUserConfig.get_all(session)
            self.__user_config_matching = {
                user_config.id: user_config for user_config in user_configs
            }

    @contextlib.contextmanager
    def user_config_session(self, user_id: int) -> UserConfig:
        def save_config(config: UserConfig) -> None:
            self.__user_config_matching[user_id] = config
            with open_session() as session:
                DBUserConfig.save_config(user_config=config, session=session)

        if user_id not in self.__user_config_matching.keys():
            new_config = UserConfig(id=user_id)
            save_config(new_config)

        old_config = self.__user_config_matching[user_id]
        new_config = deepcopy(old_config)
        yield new_config

        if new_config != old_config:
            save_config(new_config)

    def get_user_config_matching_copy(self) -> dict[int, UserConfig]:
        return deepcopy(self.__user_config_matching)


bot_context = BotContext()
