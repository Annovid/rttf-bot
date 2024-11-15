import re
import unittest
from pathlib import Path

import pytest
from bs4 import BeautifulSoup

from parsers.tournaments_parser import TournamentsParser


def get_test_cases() -> list[pytest.param]:
    return [
        pytest.param(
            str(file_path),
            id=str(file_path).split("/")[-1].split(".")[0],
        )
        for file_path in Path("static/htmls/2024-11-09/ts").rglob("*.html")
    ]


@pytest.mark.parametrize("file_path", get_test_cases())
def test_check_parsed_tournaments(file_path: str):
    with open(file_path, "r") as f:
        page = f.read()
    parser = TournamentsParser()
    tournaments = parser.parse_data(page)
    parsed_count = len(tournaments)
    soup = BeautifulSoup(page, "html.parser")
    expected_count = TournamentsParser.get_tournaments_count(soup)

    if expected_count:
        assert parsed_count == expected_count
    assert parsed_count == 100  # Из-за пагинации не получили весь день
