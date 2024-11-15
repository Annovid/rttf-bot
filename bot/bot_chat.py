# from telegram import Message
#
# from bot.bot_context import bot_context
# from clients.client import RTTFClient
# from utils.general import parse_id, get_valid_initials, get_text, parse_int
# from services.get_tournament_info import GetTournamentInfoCommand
# from parsers.players_parser import PlayersParser
# from utils.models import StateMachine, Tournament, UserConfig
# from utils.rttf import get_player_info
# from utils.settings import settings
#
#
# @bot_context.bot.message_handler(commands=['start'])
# def start(message: Message):
#     text = get_text('start.txt')
#     bot_context.bot.reply_to(message, text)
#     with bot_context.user_config_session(message.from_user.id) as user_config:  # type: UserConfig
#         user_config.state = StateMachine.MAIN
#
#
# @bot_context.bot.message_handler(commands=['help', 'back'])
# def start(message: Message):
#     text = get_text('help.txt')
#     bot_context.bot.reply_to(message, text)
#     with bot_context.user_config_session(message.from_user.id) as user_config:  # type: UserConfig
#         user_config.state = StateMachine.MAIN
#
#
# @bot_context.bot.message_handler(commands=['add_friend'])
# def add_friend(message: Message):
#     bot_context.bot.reply_to(
#         message,
#         'Вы можете добавить друга по *фамилии и имени*, *ID* на сайте RTTF или с '
#         'помощью *ссылки на его профиль*. '
#         'Чтобы добавить друга по *фамилии и имени*, введите сначала фамилию, '
#         'затем имя. '
#         'Если хотите добавить пользователя по *ID* или *ссылке на его профиль,* введите'
#         'ID или ссылку на профиль. '
#         'Например, 168970 или https://m.rttf.ru/players/168970',
#     )
#     with bot_context.user_config_session(message.from_user.id) as user_config:  # type: UserConfig
#         user_config.state = StateMachine.ADD_FRIEND
#
#
# @bot_context.bot.message_handler(commands=['get_friends'])
# def get_friends(message: Message):
#     with bot_context.user_config_session(message.from_user.id) as user_config:  # type: UserConfig
#         friend_ids = user_config.friend_ids
#     if not friend_ids:
#         bot_context.bot.reply_to(
#             message,
#             'У вас пока нет друзей. Вы можете добавить друга с помощью команды'
#             '/add\_friend',
#         )
#         return
#     reply_text = f'Список ваших друзей:\n\n'
#     for friend_id in friend_ids:
#         player = get_player_info(friend_id)
#         reply_text += player.to_md() + '\n\n'
#     bot_context.bot.reply_to(message, reply_text)
#
#
# @bot_context.bot.message_handler(commands=['delete_friend'])
# def delete_friend(message: Message):
#     with bot_context.user_config_session(message.from_user.id) as user_config:  # type: UserConfig
#         friend_ids = user_config.friend_ids
#     if not friend_ids:
#         bot_context.bot.reply_to(
#             message,
#             f'У вас нет друзей (\n'
#             f'Если хотите удалить друзей, сначала их добавьте с помощью '
#             f'команды /add\_friend',
#         )
#         with bot_context.user_config_session(message.from_user.id) as user_config:  # type: UserConfig
#             user_config.state = StateMachine.MAIN
#             return
#     reply_message = 'Кликните на ID друга, которого хотите удалить: \n\n'
#     for friend_id in friend_ids:
#         friend = get_player_info(friend_id)
#         reply_message += friend.to_md2() + '\n\n'
#     bot_context.bot.reply_to(message, reply_message)
#     with bot_context.user_config_session(message.from_user.id) as user_config:  # type: UserConfig
#         user_config.state = StateMachine.DELETE_FRIEND
#
#
# def get_match_representation_md(player_id: int, tournament: Tournament) -> str:
#     player = get_player_info(player_id)
#     msg = (
#         f'Ваш друг {player.to_md_one_str()} '
#         f'будет участвовать в турнире {tournament.to_md_one_str()}'
#     )
#     return msg
#
#
# @bot_context.bot.message_handler(commands=['get_tournaments_info'])
# def get_tournaments_info(message: Message):
#     with bot_context.user_config_session(message.from_user.id) as user_config:  # type: UserConfig
#         friend_ids = user_config.friend_ids
#     if not friend_ids:
#         bot_context.bot.reply_to(
#             message,
#             'Вы ещё не добавили друзей. Чтобы добавить друзей, воспользуйтесь командой /add\_friend',
#         )
#         return
#     bot_context.bot.reply_to(
#         message,
#         'Собираем статистику по всем турнирам в ближайшее время. '
#         'Это может занять до одной минуты. Подождите, пожалуйста...',
#     )
#     info = GetTournamentInfoCommand().get_tournament_info(friend_ids)
#     if not info:
#         bot_context.bot.reply_to(message, 'Ваши друзья пока не записались на турниры.')
#         return
#     msg = 'Список друзей, которые будут играть в турнирах в ближайшие несколько дней:\n'
#     for player_id, tournaments in info.items():
#         for tournament in tournaments:
#             match_representation = get_match_representation_md(player_id, tournament)
#             msg += '---\n' + match_representation + '\n'
#     bot_context.bot.reply_to(message, msg)
#
#
# @bot_context.bot.message_handler(commands=['load_user_config_matching'])
# def load_user_config_matching(message: Message):
#     with bot_context.user_config_session(message.from_user.id) as user_config:  # type: UserConfig
#         user_state = user_config.state
#     if user_state != StateMachine.ADMIN:
#         return
#     bot_context.load_user_config_matching()
#     bot_context.bot.reply_to(message, 'С-с-сделано.')
#
#
# @bot_context.bot.message_handler(commands=['get_user_ids'])
# def get_user_ids(message: Message):
#     with bot_context.user_config_session(message.from_user.id) as user_config:  # type: UserConfig
#         user_state = user_config.state
#     if user_state != StateMachine.ADMIN:
#         return
#     user_ids = bot_context.get_user_config_matching_copy().keys()
#     reply_message = ', '.join(map(str, user_ids))
#     bot_context.bot.reply_to(message, reply_message)
#
#
# @bot_context.bot.message_handler(commands=['get_user_config'])
# def get_user_config(message: Message):
#     with bot_context.user_config_session(message.from_user.id) as user_config:  # type: UserConfig
#         user_state = user_config.state
#     if user_state != StateMachine.ADMIN:
#         return
#     user_id = parse_int(message.text[17:])
#     user_config = bot_context.get_user_config_matching_copy().get(user_id, None)
#     bot_context.bot.reply_to(message, f'```\n{str(user_config)}\n```', parse_mode=None)
#
#
# @bot_context.bot.message_handler(func=lambda message: True)
# def answer_to_message(message: Message):
#     with bot_context.user_config_session(message.from_user.id) as user_config:  # type: UserConfig
#         if message.text == settings.ADMIN_PASSWORD:
#             if user_config.state == StateMachine.ADMIN:
#                 user_config.state = StateMachine.MAIN
#                 bot_context.bot.reply_to(message, f'Вы вышли из режима админа.')
#                 return
#             user_config.state = StateMachine.ADMIN
#             bot_context.bot.reply_to(message, get_text('admin.txt'))
#
#     with bot_context.user_config_session(message.from_user.id) as user_config:  # type: UserConfig
#         user_state = user_config.state
#     if user_state == StateMachine.MAIN:
#         bot_context.bot.reply_to(
#             message, 'Чтобы узнать о возможностях бота, введите команду /help.'
#         )
#     if user_state == StateMachine.ADD_FRIEND:
#         if friend_id := parse_id(message.text):
#             already_in_friends = False
#             with bot_context.user_config_session(message.from_user.id) as user_config:  # type: UserConfig
#                 if friend_id in user_config.friend_ids:
#                     already_in_friends = True
#                 else:
#                     user_config.friend_ids.add(friend_id)
#                 user_config.state = StateMachine.MAIN
#             player = get_player_info(friend_id)
#             if already_in_friends:
#                 bot_context.bot.reply_to(
#                     message, f'У вас уже есть друг {player.to_md_one_str()}.'
#                 )
#             else:
#                 bot_context.bot.reply_to(
#                     message, f'Друг {player.to_md_one_str()} успешно добавлен.'
#                 )
#             return
#         if search_str := get_valid_initials(message.text):
#             players_page = RTTFClient.get_players(search_str)
#             players = PlayersParser().parse_data(players_page)
#             if len(players) == 0:
#                 bot_context.bot.reply_to(
#                     message,
#                     f'К сожалению, никто не найден (\n'
#                     f'Попробуйте ещё раз. '
#                     f'Если больше не хотите добавлять друзей, введите /back',
#                 )
#                 return
#             ans_message = (
#                 'Есть ли среди приведённых ниже людей ваш друг? '
#                 'Если да, кликните на его ID.\n'
#                 'Если нет, попробуйте ввести его инициалы ещё раз. '
#                 'И помните: сначала фамилия, затем имя!\n\n'
#                 'Если больше не хотите добавлять друзей, введите /start\n\n'
#             )
#
#             for player in players:
#                 ans_message += '---\n' + player.to_md2() + '\n'
#
#             bot_context.bot.reply_to(message, ans_message)
#             return
#         else:
#             bot_context.bot.reply_to(
#                 message,
#                 'Пожалуйста, введите корректный ID или ссылку на друга. '
#                 'Если больше не хотите добавлять друзей, введите /start',
#             )
#     elif user_state == StateMachine.DELETE_FRIEND:
#         if friend_id := parse_id(message.text):
#             was_in_friends = True
#             with bot_context.user_config_session(message.from_user.id) as user_config:  # type: UserConfig
#                 if friend_id in user_config.friend_ids:
#                     user_config.friend_ids.discard(friend_id)
#                 else:
#                     was_in_friends = False
#                 user_config.state = StateMachine.MAIN
#             if was_in_friends:
#                 bot_context.bot.reply_to(
#                     message, f'Друг с ID {friend_id} успешно удалён.'
#                 )
#             else:
#                 bot_context.bot.reply_to(
#                     message, f'У вас и так нет друга с ID {friend_id}.'
#                 )
#         else:
#             bot_context.bot.reply_to(
#                 message,
#                 'Пожалуйста, введите корректный ID или ссылку на друга.',
#             )
#
#
# if __name__ == '__main__':
#     bot_context.bot.infinity_polling()
