from typing import Callable

from bot.handlers.answer_to_message import main, add_friend, delete_friend
from clients.client import RTTFClient
from parsers.players_parser import PlayersParser
from telebot.types import Message
from bot.bot_context import BotContext, extended_message_handler
from utils.custom_logger import logger
from utils.general import get_text, parse_id, get_valid_initials
from utils.models import StateMachine
from utils.rttf import get_player_info
from utils.settings import settings


STATE_COMMAND_MATCHING: dict[
    StateMachine, Callable[[BotContext, Message], StateMachine | None]
] = {
    StateMachine.MAIN: main.answer,
    StateMachine.ADD_FRIEND: add_friend.answer,
    StateMachine.DELETE_FRIEND: delete_friend.answer,
}


def register_handlers(bot_context: BotContext):
    bot = bot_context.bot
    message_handler = extended_message_handler(bot.message_handler)

    def handle_admin(message: Message):
        with bot_context.user_config_session(message.from_user.id) as user_config:  # type: UserConfig
            if user_config.state == StateMachine.ADMIN:
                user_config.state = StateMachine.MAIN
                bot_context.bot.reply_to(message, f'Вы вышли из режима админа.')
                return
            user_config.state = StateMachine.ADMIN
            bot_context.bot.reply_to(message, get_text('admin.txt'))

    @message_handler(func=lambda message: True)
    def answer_to_message(message: Message):
        if message.text == settings.ADMIN_PASSWORD:
            handle_admin(message)
            return

        with bot_context.user_config_session(message.from_user.id) as user_config:  # type: UserConfig
            user_state = user_config.state
        command: Callable[[BotContext, Message], None] | None = (
            STATE_COMMAND_MATCHING.get(user_state)
        )
        if command is None:
            logger.warning('Command for this state machine is not yet implemented yet.')
            return
        new_state_machine: StateMachine | None = command(bot_context, message)
        if new_state_machine is not None:
            with bot_context.user_config_session(message.from_user.id) as user_config:  # type: UserConfig
                user_config.state = new_state_machine
