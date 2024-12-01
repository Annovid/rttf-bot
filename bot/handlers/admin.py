from telegram import Message
from bot.bot_context import BotContext
from utils.general import parse_int
from utils.models import StateMachine


def register_handlers(bot_context: BotContext):
    bot = bot_context.bot

    @bot.message_handler(commands=['load_user_config_matching'])
    def load_user_config_matching(message: Message):
        with bot_context.user_config_session(message.from_user.id) as user_config:  # type: UserConfig
            user_state = user_config.state
        if user_state != StateMachine.ADMIN:
            return
        bot_context.load_user_config_matching()
        bot_context.bot.reply_to(message, 'С-с-сделано.')

    @bot_context.bot.message_handler(commands=['get_user_ids'])
    def get_user_ids(message: Message):
        with bot_context.user_config_session(message.from_user.id) as user_config:  # type: UserConfig
            user_state = user_config.state
        if user_state != StateMachine.ADMIN:
            return
        user_ids = bot_context.get_user_config_matching_copy().keys()
        reply_message = ', '.join(map(str, user_ids))
        bot_context.bot.reply_to(message, reply_message)

    @bot_context.bot.message_handler(commands=['get_user_config'])
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
