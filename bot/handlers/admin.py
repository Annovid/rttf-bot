from telebot.types import Message
from bot.bot_context import BotContext, extended_message_handler
from utils.general import parse_int
from utils.models import StateMachine


def register_handlers(bot_context: BotContext):
    bot = bot_context.bot
    message_handler = extended_message_handler(bot.message_handler)

    @message_handler(commands=['get_user_ids'])
    def get_user_ids(message: Message):
        with bot_context.user_config_session(message.from_user.id) as user_config:  # type: UserConfig
            user_state = user_config.state
        if user_state != StateMachine.ADMIN:
            return
        user_ids = bot_context.get_user_config_matching_copy().keys()
        reply_message = ', '.join(map(str, user_ids))
        bot_context.bot.reply_to(message, reply_message)

    @message_handler(commands=['get_user_config'])
    def get_user_config(message: Message):
        with bot_context.user_config_session(message.from_user.id) as user_config:  # type: UserConfig
            user_state = user_config.state
        if user_state != StateMachine.ADMIN:
            return
        user_id = parse_int(message.text[17:])
        user_config = bot_context.get_user_config_matching_copy().get(user_id, None)
        bot_context.bot.reply_to(
            message, f'```\n{str(user_config)}\n```', parse_mode=None
        )
