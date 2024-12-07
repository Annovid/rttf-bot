from telebot.types import Message

from bot.bot_context import extended_message_handler, BotContext
from utils.general import get_text
from utils.models import StateMachine


def register_handlers(bot_context: BotContext) -> None:
    message_handler = extended_message_handler(bot_context.bot.message_handler)

    @message_handler(commands=['start'])
    def start(message: Message):
        text = get_text('start.txt')
        bot_context.bot.reply_to(message, text)
        user_config = bot_context.user_config_service.get_user_config(message.from_user.id)
        user_config.state = StateMachine.MAIN
        bot_context.user_config_service.save_user_config()

    @message_handler(commands=['help', 'back'])
    def help_or_back(message: Message):
        text = get_text('help.txt')
        bot_context.bot.reply_to(message, text)
        user_config = bot_context.user_config_service.get_user_config(message.from_user.id)
        user_config.state = StateMachine.MAIN
        bot_context.user_config_service.save_user_config()
