from telegram import Message

from bot.bot_context import bot_context
from clients.client import RTTFClient
from utils.general import parse_id, get_valid_initials, get_text
from commands.get_tournament_info import GetTournamentInfoCommand
from parsers.players_parser import PlayersParser
from utils.models import StateMachine


@bot_context.bot.message_handler(commands=["start"])
def start(message: Message):
    text = get_text("start.txt")
    bot_context.bot.reply_to(message, text)
    with bot_context.user_config_session(message.from_user.id) as user_config:
        user_config.state = StateMachine.MAIN


@bot_context.bot.message_handler(commands=["add_friend"])
def add_friend(message: Message):
    bot_context.bot.reply_to(
        message,
        "Введите id друга, которого хотите добавить или ссылку на него. "
        "Например, 168970 или https://m.rttf.ru/players/168970. Если не знаете"
        "его профиля, можете поискать по имени и фамилии. "
        "В этом случае важно вписать сначала фамилию, затем имя.",
    )
    with bot_context.user_config_session(message.from_user.id) as user_config:
        user_config.state = StateMachine.ADD_FRIEND


@bot_context.bot.message_handler(commands=["get_friends"])
def get_friends(message: Message):
    with bot_context.user_config_session(message.from_user.id) as user_config:
        friend_ids = user_config.friend_ids
    bot_context.bot.reply_to(message, f"Список ваших друзей: {friend_ids}")


@bot_context.bot.message_handler(commands=["delete_friend"])
def delete_friend(message: Message):
    with bot_context.user_config_session(message.from_user.id) as user_config:
        friend_ids = user_config.friend_ids
    if not friend_ids:
        bot_context.bot.reply_to(
            message,
            f"У вас нет друзей (\n"
            f"Если хотите удалить друзей, сначала их добавьте с помощью команды /add\_friend"
        )
        with bot_context.user_config_session(message.from_user.id) as user_config:
            user_config.state = StateMachine.MAIN
            return
    bot_context.bot.reply_to(
        message,
        f"Введите id друга, которого хотите удалить. Список ваших друзей: {friend_ids}."
    )
    with bot_context.user_config_session(message.from_user.id) as user_config:
        user_config.state = StateMachine.DELETE_FRIEND


@bot_context.bot.message_handler(commands=["get_tournaments_info"])
def get_tournaments_info(message: Message):
    with bot_context.user_config_session(message.from_user.id) as user_config:
        friend_ids = user_config.friend_ids
    if not friend_ids:
        bot_context.bot.reply_to(
            message,
            "Вы ещё не добавили друзей. Чтобы добавить друзей, воспользуйтесь командой /add\_friend",
        )
        return
    bot_context.bot.reply_to(
        message,
        "Собираем статистику по всем турнирам в ближайшее время. "
        "Это может занять до одной минуты. Подождите, пожалуйста..."
    )
    info = GetTournamentInfoCommand().get_tournament_info(friend_ids)
    if not info:
        bot_context.bot.reply_to(message, "Ваши друзья пока не записались на турниры.")
        return
    msg = "Список друзей, которые будут играть в турнирах в ближайшие несколько дней:\n"
    for player_id, tournament_id in info.items():
        one_str = (
            f"Друг "
            f"[{player_id}](https://m.rttf.ru/players/{player_id}) "
            f"будет участвовать в турнире "
            f"[{tournament_id}](https://m.rttf.ru/tournaments/{tournament_id})\n")
        msg += one_str
    bot_context.bot.reply_to(message, msg)


@bot_context.bot.message_handler(func=lambda message: True)
def answer_to_message(message: Message):
    with bot_context.user_config_session(message.from_user.id) as user_config:
        user_state = user_config.state
    if user_state == StateMachine.MAIN:
        bot_context.bot.reply_to(
            message, "Чтобы узнать о возможностях бота, введите команду /start."
        )
    if user_state == StateMachine.ADD_FRIEND:
        if friend_id := parse_id(message.text):
            already_in_friends = False
            with bot_context.user_config_session(message.from_user.id) as user_config:
                if friend_id in user_config.friend_ids:
                    already_in_friends = True
                else:
                    user_config.friend_ids.add(friend_id)
                user_config.state = StateMachine.MAIN
            if already_in_friends:
                bot_context.bot.reply_to(
                    message, f"У вас уже есть друг с ID {friend_id}."
                )
            else:
                bot_context.bot.reply_to(
                    message, f"Друг с ID {friend_id} успешно добавлен."
                )
            return
        if search_str := get_valid_initials(message.text):
            players_page = RTTFClient.get_players(search_str)
            players = PlayersParser().parse_data(players_page)
            if len(players) == 0:
                bot_context.bot.reply_to(
                    message,
                    f"К сожалению, никто не найден (\n"
                    f"Попробуйте ещё раз. "
                    f"Если больше не хотите добавлять друзей, введите /start",
                )
                return
            ans_message = (
                "Есть ли среди приведённых ниже людей ваш друг? Если да, введите его id.\n"
                "Если нет, попробуйте ввести его инициалы ещё раз. "
                "И помните: сначала фамилия, затем имя!\n\n"
                "Если больше не хотите добавлять друзей, введите /start\n\n"
            )

            # Заголовок таблицы
            ans_message += "| Ранг | Имя                | Город        | Рейтинг | Профиль            |\n"
            ans_message += "|------|--------------------|--------------|---------|--------------------|\n"

            # Данные игроков
            for player in players:
                player_str = (
                    f"| {player['rank']:<4} | "
                    f"{player['name']:<18} | "
                    f"{player['city']:<12} | "
                    f"{player['rating']:<7} | "
                    f"[Профиль]({player['profile_link']}) |\n"
                )
                ans_message += player_str

            bot_context.bot.reply_to(message, ans_message)
            return
        else:
            bot_context.bot.reply_to(
                message,
                "Пожалуйста, введите корректный ID или ссылку на друга. "
                "Если больше не хотите добавлять друзей, введите /start",
            )
    elif user_state == StateMachine.DELETE_FRIEND:
        if friend_id := parse_id(message.text):
            was_in_friends = True
            with bot_context.user_config_session(message.from_user.id) as user_config:
                if friend_id in user_config.friend_ids:
                    user_config.friend_ids.discard(friend_id)
                else:
                    was_in_friends = False
                user_config.state = StateMachine.MAIN
            if was_in_friends:
                bot_context.bot.reply_to(message, f"Друг с ID {friend_id} успешно удалён.")
            else:
                bot_context.bot.reply_to(message, f"У вас и так нет друга с ID {friend_id}.")
        else:
            bot_context.bot.reply_to(
                message,
                "Пожалуйста, введите корректный ID или ссылку на друга.",
            )


if __name__ == "__main__":
    bot_context.bot.infinity_polling()
