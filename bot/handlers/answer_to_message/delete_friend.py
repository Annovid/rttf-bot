from bot.bot_context import BotContext
from clients.client import RTTFClient
from parsers.players_parser import PlayersParser
from telebot.types import Message
from utils.general import parse_id, get_valid_initials
from utils.models import StateMachine
from utils.rttf import get_player_info


def answer(bot_context: BotContext, message: Message) -> StateMachine | None:
    if friend_id := parse_id(message.text):
        was_in_friends = True
        with bot_context.user_config_session(message.from_user.id) as user_config:  # type: UserConfig
            if friend_id in user_config.friend_ids:
                user_config.friend_ids.discard(friend_id)
            else:
                was_in_friends = False
            user_config.state = StateMachine.MAIN
        if was_in_friends:
            bot_context.bot.reply_to(message, f'Друг с ID {friend_id} успешно удалён.')
        else:
            bot_context.bot.reply_to(
                message, f'У вас и так нет друга с ID {friend_id}.'
            )
    else:
        bot_context.bot.reply_to(
            message,
            'Пожалуйста, введите корректный ID или ссылку на друга.',
        )
    return None
