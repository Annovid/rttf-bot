from bot.bot_context import BotContext
from clients.client import RTTFClient
from parsers.players_parser import PlayersParser
from telegram import Message
from utils.custom_logger import logger
from utils.general import parse_id, get_valid_initials
from utils.models import StateMachine
from utils.rttf import get_player_info


def answer(bot_context: BotContext, message: Message) -> StateMachine | None:
    if friend_id := parse_id(message.text):
        already_in_friends = False
        with bot_context.user_config_session(message.from_user.id) as user_config:  # type: UserConfig
            if friend_id in user_config.friend_ids:
                already_in_friends = True
            else:
                user_config.friend_ids.add(friend_id)
            user_config.state = StateMachine.MAIN
        try:
            player = get_player_info(friend_id)
        except Exception:
            logger.warning(
                'Exception while getting player_info for friend_id %s', friend_id
            )
            bot_context.bot.reply_to(
                message,
                f'Не найден пользователь с ID = {friend_id}. Попробуйте найти друга по *Фамилии и имени*.',
            )
            return
        if already_in_friends:
            bot_context.bot.reply_to(
                message, f'У вас уже есть друг {player.to_md_one_str()}.'
            )
        else:
            bot_context.bot.reply_to(
                message, f'Друг {player.to_md_one_str()} успешно добавлен.'
            )
        return
    if search_str := get_valid_initials(message.text):
        players_page = RTTFClient.get_players(search_str)
        players = PlayersParser().parse_data(players_page)
        if len(players) == 0:
            bot_context.bot.reply_to(
                message,
                f'К сожалению, никто не найден (\n'
                f'Попробуйте ещё раз. '
                f'Если больше не хотите добавлять друзей, введите /back',
            )
            return
        ans_message = (
            'Есть ли среди приведённых ниже людей ваш друг? '
            'Если да, кликните на его ID.\n'
            'Если нет, попробуйте ввести его инициалы ещё раз. '
            'И помните: сначала фамилия, затем имя!\n\n'
            'Если больше не хотите добавлять друзей, введите /start\n\n'
        )

        for player in players:
            ans_message += '---\n' + player.to_md2() + '\n'

        bot_context.bot.reply_to(message, ans_message)
        return
    else:
        bot_context.bot.reply_to(
            message,
            'Пожалуйста, введите корректный ID или ссылку на друга. '
            'Если больше не хотите добавлять друзей, введите /start',
        )
