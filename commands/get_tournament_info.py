import re
import time

from collections import defaultdict
from multiprocessing.pool import ThreadPool

from clients.client import RTTFClient
from parsers.tournament_parser import TournamentParser
from parsers.tournaments_parser import TournamentsParser
from utils.custom_logger import custom_logger
from utils.models import DateRange, Tournament
from utils.settings import settings


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
        with ThreadPool(settings.MAX_WORKERS) as pool:
            tournaments_parse_result = pool.map(
                TournamentsParser.parse_data, tournaments_page
            )

        tournaments_parse_result = [
            result
            for sublist in tournaments_parse_result
            for result in sublist
        ]

        if not tournaments_parse_result:
            custom_logger.warning("Tournaments were not found")
            return {}

        for tournament in tournaments_parse_result:
            sub_matching = self.process_tournament(tournament, friend_ids)
            for friend_id, tournament in sub_matching:
                matchings[friend_id].append(tournament)
        return matchings

    @classmethod
    def process_tournament(
        cls, tournament_parse_result, friend_ids: set[int]
    ) -> list[tuple[int, Tournament]]:
        tournament_page = RTTFClient.get_tournament(tournament_parse_result.id)
        tournament = TournamentParser.parse_data(tournament_page)
        if tournament is None:
            custom_logger.warning("Tournament was not found")
            return []
        player_matches = []
        for player in tournament.registered_players:
            if player.id in friend_ids:
                player_matches.append((player.id, tournament))
        return player_matches

    @classmethod
    def get_tournament_data(cls, tournament_id):
        tournament_page = RTTFClient.get_tournament(tournament_id)
        return TournamentParser.parse_data(tournament_page)


def main():
    timestamp_start = time.time()
    matchings = GetTournamentInfoCommand().get_tournament_info(
        friend_ids={168970},
        date_range=DateRange(
            days_from=0,
            days_to=0,
        ),
    )
    timestamp_end = time.time()
    execution_time = timestamp_end - timestamp_start
    print(f"Выполнение команды заняло {execution_time:.4f} секунд")
    print(matchings)


if __name__ == "__main__":
    main()
