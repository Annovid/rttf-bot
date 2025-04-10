from parsers.tournament_parser import TournamentParser
from utils.models import Tournament

def test_parse_player_results():
    with open('htmls/2024-11-02/passed_pers.html', 'r') as f:
        page = f.read()
    parse_result: Tournament = TournamentParser().parse_data(page)
    assert len(parse_result.player_results) > 0
    # Берем второго игрока, т.к. у первого lost = 0, плохо для теста)
    assert parse_result.player_results[1].player_id > 0
    assert parse_result.player_results[1].rating_before > 0
    assert parse_result.player_results[1].rating_delta > 0
    assert parse_result.player_results[1].games_won > 0
    assert parse_result.player_results[1].games_lost > 0