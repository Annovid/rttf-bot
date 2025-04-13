from bot.bot_context import BotContext
from clients.client import RTTFClient
from parsers.players_parser import PlayersParser
from telebot.types import Message
from utils.custom_logger import logger
from utils.general import parse_id, get_valid_initials
from utils.models import StateMachine, Player
from utils.rttf import get_player_info


def fetch_and_parse_players(search_str: str) -> list[Player]:
    """
    Метод для получения и парсинга данных игроков.
    Логирует процесс запроса, получения и выдачи данных.
    """
    logger.info(f'Requested players for search string: {search_str}')
    # Получение данных для исходного поискового запроса
    players_page = RTTFClient.get_players(search_str)
    logger.info(f'Received players page for search string: {search_str}')
    # Парсинг данных
    players = PlayersParser().parse_data(players_page)
    logger.info(f'Parsed players for search string: {search_str}')

    # Если поисковый запрос содержит два слова, выполняем поиск с обратным порядком слов
    if len(search_str.split(' ')) == 2:
        search_str_new = ' '.join(search_str.split(' ')[::-1])
        logger.info(f'Requested players for reversed search string: {search_str_new}')
        players_page_new = RTTFClient.get_players(search_str_new)
        players_new = PlayersParser().parse_data(players_page_new)
        logger.info(f'Parsed players for reversed search string: {search_str_new}')

        # Объединяем результаты
        players = players_new[:6] + players[:6]

    logger.info(f'Returned players for search string: {search_str}')
    return players


def answer(bot_context: BotContext, message: Message) -> StateMachine | None:
    if friend_id := parse_id(message.text):
        already_in_friends = False
        with bot_context.user_config_session(message) as user_config:
            if friend_id in user_config.friend_ids:
                already_in_friends = True
            user_config.state = StateMachine.MAIN
        try:
            player = get_player_info(friend_id)
            with bot_context.user_config_session(message) as user_config:
                user_config.friend_ids.add(friend_id)
        except Exception:  # noqa
            logger.warning(
                'Exception while getting player_info for friend_id %s', friend_id
            )
            bot_context.bot.reply_to(
                message,
                f'Не найден пользователь с ID = {friend_id}. '
                f'Попробуйте найти друга по *Фамилии и имени*. '
                f'Вы также можете узнать о возможных функциях с помощью метода /start',
            )
            return StateMachine.ADD_FRIEND
        if already_in_friends:
            bot_context.bot.reply_to(
                message,
                f'У вас уже есть друг {player.to_md_one_str()}. '
                f'Если хотите ещё раз попытаться добавить друга, введите /add\_friend. '  # noqa
                f'Вы также можете узнать о возможных функциях с помощью метода /start',
            )
        else:
            bot_context.bot.reply_to(
                message,
                f'Друг {player.to_md_one_str()} успешно добавлен. '
                f'Если хотите добавить ещё одного друга, введите /add\_friend. '  # noqa
                f'Вы также можете узнать о возможных функциях с помощью метода /start',
            )
        return
    if search_str := get_valid_initials(message.text):
        players = fetch_and_parse_players(search_str)
        if len(players) == 0:
            bot_context.bot.reply_to(
                message,
                'К сожалению, никто не найден (\n'
                'Попробуйте ещё раз. '
                'Если больше не хотите добавлять друзей, введите /start',
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
