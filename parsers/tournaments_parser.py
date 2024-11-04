import logging

from bs4 import BeautifulSoup

import datetime
from pydantic import BaseModel, Field

from parsers.parser import Parser
from utils.models import Tournament


class TournamentParseResult(BaseModel):
    id: int = Field(description="Tournament ID")
    datetime: str = Field(description="Tournament datetime")
    name: str = Field(str, description="Name of the tournament")
    players: str = Field(
        int, description="Players participating in the tournament"
    )
    rating: str | None = Field(
        int, description="Mean rating of the tournament"
    )
    type: str = Field(int | None, description="Max rating")


def transform_dict_for_tr(data: dict) -> dict:
    # TODO: Переделать
    data["id"] = data["link"].split("/")[1]

    date_str = data["date"].split(" / ")[0]  # Get only the date part
    time_str = data["time"]
    datetime_str = f"{date_str} {time_str}"
    dt = datetime.datetime.strptime(datetime_str, "%d.%m.%Y %H:%M")
    data["datetime"] = dt.strftime("%Y-%m-%d %H:%M")
    return data


class TournamentsParser(Parser):
    @classmethod
    def _parse_data(cls, page: str) -> list[TournamentParseResult]:
        soup = BeautifulSoup(page, "html.parser")
        tbody = soup.find("table")
        if not tbody:
            raise ValueError("Unable to find tournaments section.")

        tournaments = []
        current_date = None

        for row in tbody.find_all("tr"):
            if cls._is_date_row(row):
                current_date = cls._parse_date(row)
                continue

            if cls._is_tournament_row(row):
                tournament = cls._parse_tournament(row, current_date)
                tournaments.append(TournamentParseResult(**tournament))

        return tournaments

    @classmethod
    def _is_date_row(cls, row):
        """Проверяет, является ли строка датой."""
        return "class" in row.attrs and "date" in row["class"]

    @classmethod
    def _parse_date(cls, row):
        """Парсит строку с датой."""
        date_col = row.find("th", colspan="3")
        if date_col:
            return date_col.text.strip()
        raise ValueError("Unable to parse date row")

    @classmethod
    def _is_tournament_row(cls, row):
        """Проверяет, является ли строка турниром."""
        return "class" in row.attrs and "reg" in row["class"]

    @classmethod
    def _parse_tournament(cls, row, current_date):
        """Парсит строку с турниром и возвращает словарь с данными."""
        if current_date is None:
            raise RuntimeError("current_date is None")

        time = row.find("td").text.strip()
        tournament_type = row.find("var").text.strip()
        name = row.find("a").text.strip()
        link = row.find("a")["href"]
        rating = row.find("dfn").text.strip() if row.find("dfn") else None
        players = row.find("kbd").text.strip()

        tournament_dict = {
            "date": current_date,
            "time": time,
            "type": tournament_type,
            "name": name,
            "link": link,
            "rating": rating,
            "players": players,
        }

        return transform_dict_for_tr(tournament_dict)


def main():
    with open("htmls/tournaments/tournaments.html", "r") as f:
        page = f.read()
    parse_result = TournamentsParser()._parse_data(page)
    print("\n".join(map(str, parse_result)))


if __name__ == "__main__":
    main()
