import pytest

from parsers.tournament_parser import TournamentParser
from utils.models import Tournament


@pytest.mark.parametrize(
    "filename, expected_registered_players",
    [
        pytest.param("planning_personal.html", 2, id="planning_personal.html"),
        pytest.param("completed_personal.html", 16, id="completed_personal"),
        pytest.param("ongoing_personal.html", 19, id="ongoing_personal"),
        pytest.param("ongoing_pair.html", 20, id="ongoing_pair"),
    ],
)
def test_add(filename: str, expected_registered_players: int):
    with open("static/htmls/2024-11-02/t/" + filename, "r") as f:
        page = f.read()
    tournament: Tournament = TournamentParser.parse_data(page)
    assert len(tournament.registered_players) == expected_registered_players
