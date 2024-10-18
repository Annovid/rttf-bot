import enum
import os
from collections import defaultdict

import telebot
from telegram import Message

from commands.get_tournament_info import GetTournamentInfoCommand
from utils.settings import settings


class StateMachine(enum.Enum):
    MAIN = "main_state"
    ADD_FRIEND = "add_friend_state"
    CONFIRM_ADD_FRIEND = "confirm_add_friend_state"
    DELETE_FRIEND = "delete_friend_state"
    CONFIRM_DELETE_FRIEND = "confirm_delete_friend_state"
    CHANGE_CONFIG_MODE = "change_config_mode"


class UserConfig:
    friend_ids: set[int] = set()


class Bot:
    bot = telebot.TeleBot(settings.TOKEN, parse_mode=None)
    users_config: dict[int, UserConfig] = defaultdict(UserConfig)
    player_names: dict[int, str] = {}
    state_machine: StateMachine = StateMachine.MAIN


def get_text(filename):
    filepath = os.path.join("static/texts", filename)
    with open(filepath, "r") as f:
        text = f.read()
    return text


@Bot.bot.message_handler(commands=["start"])
def start(message: Message):
    text = get_text("start.txt")
    Bot.bot.reply_to(message, text)
    Bot.state_machine = StateMachine.MAIN


@Bot.bot.message_handler(commands=["add_friend"])
def add_friend(message: Message):
    Bot.bot.reply_to(
        message,
        "Введите id друга, которого хотите добавить или ссылку на него. "
        "Например, 168970 или https://m.rttf.ru/players/168970"
    )
    Bot.state_machine = StateMachine.CONFIRM_ADD_FRIEND


@Bot.bot.message_handler(commands=["get_friends"])
def get_friends(message: Message):
    friends = Bot.users_config[message.from_user.id].friend_ids
    Bot.bot.reply_to(
        message,
        f"Список ваших друзей: {friends}"
    )


@Bot.bot.message_handler(commands=["delete_friend"])
def delete_friend(message: Message):
    Bot.bot.reply_to(
        message,
        "Введите id друга, которого хотите удалить или ссылку на него. "
        "Например, 168970 или https://m.rttf.ru/players/168970"
    )
    Bot.state_machine = StateMachine.CONFIRM_DELETE_FRIEND


@Bot.bot.message_handler(commands=["get_tournaments_info"])
def get_tournaments_info(message: Message):
    friend_ids = Bot.users_config[message.from_user.id].friend_ids
    info = GetTournamentInfoCommand().get_tournament_info(friend_ids)
    msg = "Список друзей, которые будут играть в турнирах в ближайшие несколько дней:\n"
    msg += '\n'.join(map(str, info.items()))
    Bot.bot.reply_to(message, msg)


@Bot.bot.message_handler(func=lambda message: True)
def answer_to_message(message: Message):
    if Bot.state_machine == StateMachine.CONFIRM_ADD_FRIEND:
        friend_id = message.text.strip()
        if friend_id.isdigit() or friend_id.startswith("https://m.rttf.ru/players/"):
            Bot.users_config[message.from_user.id].friend_ids.add(int(friend_id))
            Bot.bot.reply_to(message, f"Друг с ID {friend_id} успешно добавлен.")
            Bot.state_machine = StateMachine.MAIN  # Сброс состояния после добавления друга
        else:
            Bot.bot.reply_to(message, "Пожалуйста, введите корректный ID или ссылку на друга.")
    elif Bot.state_machine == StateMachine.CONFIRM_DELETE_FRIEND:
        friend_id = message.text.strip()
        if friend_id.isdigit() or friend_id.startswith("https://m.rttf.ru/players/"):
            Bot.users_config[message.from_user.id].friend_ids.discard(int(friend_id))
            Bot.bot.reply_to(message, f"Друг с ID {friend_id} успешно удалён.")
            Bot.state_machine = StateMachine.MAIN  # Сброс состояния после добавления друга
        else:
            Bot.bot.reply_to(message, "Пожалуйста, введите корректный ID или ссылку на друга.")


if __name__ == "__main__":
    Bot.bot.infinity_polling()
