from telebot.types import Message

from bot.bot_context import BotContext, extended_message_handler
from services.get_tournament_info import TournamentService
from utils.models import Tournament
from utils.rttf import get_player_info


def register_handlers(bot_context: BotContext):
    bot = bot_context.bot
    message_handler = extended_message_handler(bot.message_handler)
    tournament_service = TournamentService()

    def get_match_representation_md(player_id: int, tournament: Tournament) -> str:
        player = get_player_info(player_id)
        msg = (
            f'Ваш друг {player.to_md_one_str()} '
            f'будет участвовать в турнире {tournament.to_md_one_str()}'
        )
        return msg

    @message_handler(commands=['get_tournaments_info'])
    def get_tournaments_info(message: Message):
        with bot_context.user_config_session(message) as user_config:
            friend_ids = user_config.friend_ids
        if not friend_ids:
            bot_context.bot.reply_to(
                message,
                'Вы ещё не добавили друзей. Чтобы добавить друзей, воспользуйтесь командой /add\_friend',
            )
            return
        bot_context.bot.reply_to(
            message,
            'Собираем статистику по всем турнирам в ближайшее время. '
            'Это может занять до одной минуты. Подождите, пожалуйста...',
        )
        info = tournament_service.get_tournament_info(friend_ids)
        if not info:
            bot_context.bot.reply_to(
                message, 'Ваши друзья пока не записались на турниры.'
            )
            return
        msg = 'Список друзей, которые будут играть в турнирах в ближайшие несколько дней:\n'
        for player_id, tournaments in info.items():
            for tournament in tournaments:
                match_representation = get_match_representation_md(
                    player_id, tournament
                )
                msg += '---\n' + match_representation + '\n'
        bot_context.bot.reply_to(message, msg)
