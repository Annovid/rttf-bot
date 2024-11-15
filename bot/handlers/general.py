from telegram import Message
from bot.bot_context import BotContext
from utils.general import get_text
from utils.models import StateMachine


def register_handlers(bot_context: BotContext):
    bot = bot_context.bot

    @bot.message_handler(commands=['start'])
    def start(message: Message):
        text = get_text('start.txt')
        bot.reply_to(message, text)
        with bot_context.user_config_session(message.from_user.id) as user_config:
            user_config.state = StateMachine.MAIN

    @bot.message_handler(commands=['help', 'back'])
    def help_or_back(message: Message):
        text = get_text('help.txt')
        bot.reply_to(message, text)
        with bot_context.user_config_session(message.from_user.id) as user_config:
            user_config.state = StateMachine.MAIN
