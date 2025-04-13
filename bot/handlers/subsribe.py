import logging
from telebot.types import Message
from bot.bot_context import BotContext, bot_context, extended_message_handler
from services.user_service import UserService
from utils.models import UserConfig

def register_handlers(bot_context: BotContext):
    message_handler = extended_message_handler(bot_context.bot.message_handler)

    @message_handler(commands=['subscribe'])
    def subscribe(message: Message):
        user_id = message.from_user.id
        try:
            current_config = UserService.get_user_config(user_id)
        except Exception:
            # Create a default configuration if not existing
            current_config = UserConfig(id=user_id, username=str(user_id), friend_ids=set(), subscription_on=False)
        current_config.subscription_on = True
        UserService.save_user_config(current_config)
        bot_context.bot.send_message(message.chat.id, "Subscription enabled.")

    @message_handler(commands=['unsubscribe'])
    def unsubscribe(message: Message):
        user_id = message.from_user.id
        try:
            current_config = UserService.get_user_config(user_id)
        except Exception:
            current_config = UserConfig(id=user_id, username=str(user_id), friend_ids=set(), subscription_on=False)
        current_config.subscription_on = False
        UserService.save_user_config(current_config)
        bot_context.bot.send_message(message.chat.id, "Subscription disabled.")
