from bot.bot_context import BotContext
from telebot.types import Message


def answer(bot_context: BotContext, message: Message):
    bot_context.bot.reply_to(
        message, 'Чтобы узнать о возможностях бота, введите команду /help.'
    )
