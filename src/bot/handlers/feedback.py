from telebot.types import Message

from bot.bot_context import extended_message_handler, BotContext


def register_handlers(bot_context: BotContext) -> None:
    message_handler = extended_message_handler(bot_context.bot.message_handler)

    @message_handler(commands=['feedback'])
    def feedback(message: Message):
        bot_context.bot.reply_to(
            message,
            'Привет! 👋\n'
            'Меня зовут Нил и я создатель этого бота. '
            'Я люблю программирование и настольный теннис. '
            'Я очень благодарен вам за то, что вы пользуетесь этим ботом 💙\n'
            'Если у вас есть предложение об улучшении данного бота, фича, которую вы хотите добавить '
            'или сообщение о том, что что-то не работает, напишите мне: @Annovid. '
            'Буду рад вашему сообщению!',
        )
