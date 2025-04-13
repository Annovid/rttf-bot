from typing import Callable

from bot.handlers.answer_to_message import main, add_friend, delete_friend
from telebot.types import Message
from bot.bot_context import BotContext, extended_message_handler
from utils.custom_logger import logger
from utils.models import StateMachine


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

    @message_handler(func=lambda message: True)
    def answer_to_message(message: Message):
        with bot_context.user_config_session(message) as user_config:
            user_state = user_config.state
        command: Callable[[BotContext, Message], None] | None = (
            STATE_COMMAND_MATCHING.get(user_state)
        )
        if command is None:
            logger.warning('Command for this state machine is not yet implemented yet.')
            return
        new_state_machine: StateMachine | None = command(bot_context, message)
        if new_state_machine is not None:
            with bot_context.user_config_session(message) as user_config:
                user_config.state = new_state_machine
