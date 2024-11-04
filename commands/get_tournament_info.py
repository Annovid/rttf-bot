import re
from collections import defaultdict

from clients.client import RTTFClient
from parsers.tournament_parser import TournamentParser
from parsers.tournaments_parser import TournamentsParser
from utils.custom_logger import custom_logger
from utils.models import DateRange, Tournament


def get_player_id(profile_link: str) -> int:
    try:
        match = re.search(r"/players/(\d+)", profile_link)
    except TypeError as e:
        custom_logger.error(e)
        return -1
    if match:
        return int(match.group(1))  # Возвращаем найденный player_id как число
    raise ValueError("player_id not found in the provided link")


class GetTournamentInfoCommand:
    def get_tournament_info(
            self,
            friend_ids: set[int],
            date_range: DateRange = DateRange(),
    ) -> dict[int, list[Tournament]]:
        matchings: dict[int, list[Tournament]] = defaultdict(list)
        tournaments_page = RTTFClient.get_list_of_tournaments(
            date_from=date_range.date_from,
            date_to=date_range.date_to,
        )
        tournaments_parse_result = TournamentsParser.parse_data(tournaments_page)
        if not tournaments_parse_result:
            custom_logger.warning("Tournaments was now find")
            return {}
        for tournament_parse_result in tournaments_parse_result:
            tournament_page = RTTFClient.get_tournament(tournament_parse_result.id)
            tournament = TournamentParser.parse_data(tournament_page)
            if tournament is None:
                custom_logger.warning("Tournament was not found")
                continue
            for player in tournament.registered_players:
                if player.id in friend_ids:
                    matchings[player.id].append(tournament)
        return matchings


if __name__ == "__main__":
    GetTournamentInfoCommand().get_tournament_info({168970})
