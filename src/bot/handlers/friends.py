from telebot.types import Message

from bot.bot_context import BotContext, extended_message_handler
from utils.models import StateMachine
from utils.rttf import get_player_info


def register_handlers(bot_context: BotContext):
    message_handler = extended_message_handler(bot_context.bot.message_handler)

    @message_handler(commands=['add_friend'])
    def add_friend(message: Message):
        bot_context.bot.reply_to(
            message,
            'Вы можете добавить друга по *фамилии и имени*, *ID* на сайте RTTF или с '
            'помощью *ссылки на его профиль*. '
            'Если хотите добавить пользователя по *ID* или *ссылке на его профиль,* введите '
            'ID или ссылку на профиль. '
            'Например, 168970 или https://m.rttf.ru/players/168970',
        )
        with bot_context.user_config_session(message) as user_config:
            user_config.state = StateMachine.ADD_FRIEND

    @message_handler(commands=['get_friends'])
    def get_friends(message: Message):
        with bot_context.user_config_session(message) as user_config:
            friend_ids = user_config.friend_ids
        if not friend_ids:
            bot_context.bot.reply_to(
                message,
                'У вас пока нет друзей. Вы можете добавить друга с помощью команды '
                '/add\_friend',  # noqa
            )
            return
        reply_text = 'Список ваших друзей:\n\n'
        for friend_id in friend_ids:
            try:
                friend = get_player_info(friend_id)
            except Exception:  # noqa
                reply_text += f'Друг с ID = {friend_id} не найден\n\n'
            else:
                reply_text += friend.to_md2() + '\n\n'
        bot_context.bot.reply_to(message, reply_text)

    @message_handler(commands=['delete_friend'])
    def delete_friend(message: Message):
        with bot_context.user_config_session(message) as user_config:
            friend_ids = user_config.friend_ids
        if not friend_ids:
            bot_context.bot.reply_to(
                message,
                'У вас нет друзей (\n'
                'Если хотите удалить друзей, сначала их добавьте с помощью '
                'команды /add\_friend',  # noqa
            )
            with bot_context.user_config_session(message) as user_config:
                user_config.state = StateMachine.MAIN
                return
        reply_message = 'Кликните на ID друга, которого хотите удалить: \n\n'
        for friend_id in friend_ids:
            try:
                friend = get_player_info(friend_id)
            except Exception:  # noqa
                reply_message += f'Друг с ID = /{friend_id} не найден\n\n'
            else:
                reply_message += friend.to_md2() + '\n\n'
        bot_context.bot.reply_to(message, reply_message)
        with bot_context.user_config_session(message) as user_config:
            user_config.state = StateMachine.DELETE_FRIEND
