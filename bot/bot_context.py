import contextlib
import time
from copy import deepcopy
from functools import wraps

import telebot

from services.user_service import UserService
from utils.custom_logger import logger
from utils.models import UserConfig
from utils.settings import settings


class BotContext:
    def __init__(self):
        self.bot: telebot.TeleBot = telebot.TeleBot(
            settings.TOKEN,
            parse_mode='Markdown',
            disable_web_page_preview=True,
        )
        self.user_config_service: UserService = UserService()

    @contextlib.contextmanager
    def user_config_session(self, message: telebot.types.Message) -> UserConfig:
        old_config = self.user_config_service.get_user_config(message.from_user.id)
        new_config = deepcopy(old_config)
        new_config.username = message.from_user.username
        new_config.full_name = message.from_user.full_name
        yield new_config
        if new_config != old_config:
            self.user_config_service.save_user_config(new_config)


def extended_message_handler(handler_decorator):
    """Обертка над bot.message_handler с добавлением кастомной логики."""

    def decorator(commands=None, **kwargs):
        def wrapper(handler_function):
            @wraps(handler_function)
            def wrapped_handler(message, *args, **kwargs_wrapped):
                start_time = time.time()
                user_id = message.from_user.id
                user_text = message.text[:100] if message.text else "<non-text content>"
                logger.info(
                    f"Handler '{handler_function.__name__}' called by user {user_id} "
                    f"with message: {user_text!r}"
                )
                try:
                    result = handler_function(message, *args, **kwargs_wrapped)
                finally:
                    elapsed_time = time.time() - start_time
                    logger.info(
                        f"Handler '{handler_function.__name__}' finished "
                        f"in {elapsed_time:.2f}s for user {user_id}"
                    )

                return result
            return handler_decorator(commands=commands, **kwargs)(wrapped_handler)
        return wrapper
    return decorator


# Initializing bot context
logger.debug('Initializing BotContext...')
bot_context = BotContext()
logger.info('BotContext initialized successfully.')
