import datetime
import re
from collections import defaultdict

from clients.client import RTTFClient
from parsers.tournament_parser import TournamentParser
from parsers.tournaments_parser import TournamentsParser
from utils.custom_logger import CustomLogger

logger = CustomLogger.setup_logger()


def get_player_id(profile_link: str) -> int:
    try:
        match = re.search(r"/players/(\d+)", profile_link)
    except TypeError as e:
        logger.error(e)
        return -1
    if match:
        return int(match.group(1))  # Возвращаем найденный player_id как число
    raise ValueError("player_id not found in the provided link")


class GetTournamentInfoCommand:
    def get_tournament_info(self, friend_ids: set[int]) -> dict:
        matchings = defaultdict(list)
        date_from = datetime.date.today()
        date_to = date_from + datetime.timedelta(days=1)
        tournaments_page = RTTFClient.get_list_of_tournaments(
            date_from=date_from,
            date_to=date_to,
        )
        parse_result = TournamentsParser.parse_data(tournaments_page)
        if not parse_result:
            logger.warning("Tournaments was now find")
            return {}
        for tournament_info in parse_result:
            tournament_page = RTTFClient.get_tournament(tournament_info.id)
            tournament = TournamentParser.parse_data(tournament_page)
            for player in tournament["registered_players"]:
                player_id = get_player_id(player["profile_link"])
                if player_id in friend_ids:
                    matchings[player_id] = tournament_info.id
        ans = {k: v for k, v in matchings.items()}
        return ans


if __name__ == "__main__":
    GetTournamentInfoCommand().get_tournament_info({168970})
