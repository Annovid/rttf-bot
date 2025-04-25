from typing import Optional

from bot.bot_context import BotContext
from utils.models import Player, PlayerTournamentInfo, Tournament


def send_player_update(
    user_id: int, info: PlayerTournamentInfo, bot_context: Optional[BotContext] = None
) -> str:
    player = Player(id=info.player_id, name=info.player_name)
    tournament = Tournament(id=info.tournament_id, name=info.tournament_name)
    if info.status == 'registered':
        msg = f'{player.to_md_one_str()} зарегистрирован на турнир {tournament.to_md_one_str()}'
    elif info.status == 'refused':
        msg = f'{player.to_md_one_str()} снялся с турнира {tournament.to_md_one_str()}'
    elif info.status == 'completed':
        msg = (
            f'{player.to_md_one_str()} выступил на турнире {tournament.to_md_one_str()}. '
            f'Рейтинг до: {info.rating_before}. Дельта {info.rating_delta}. '
            f'Новый рейтинг: {info.rating_after}. Игры ({info.games_won}-{info.games_lost})'
        )
    else:
        raise ValueError('Неожиданное значение статуса')
    if bot_context is not None:
        bot_context.bot.send_message(user_id, msg)
    return msg
