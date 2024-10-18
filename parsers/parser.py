import logging
from typing import Dict, List

from bs4 import BeautifulSoup


class TournamentParser:
    base_url = "https://m.rttf.ru/"

    @classmethod
    def parse_data(cls, page: str):
        try:
            return cls._parse_data(page)
        except Exception as e:
            logging.error(f"Error while parsing page: {e}")
            return None

    @classmethod
    def _parse_data(cls, page: str):
        soup = BeautifulSoup(page, "html.parser")

        # Список участников
        players = cls._parse_registered_players(soup)
        # Список снявшихся участников
        withdrawn_players = cls._parse_withdrawn_players(soup)

        return {
            "registered_players": players,
            "withdrawn_players": withdrawn_players,
        }

    @classmethod
    def _parse_registered_players(cls, soup: BeautifulSoup) -> List[Dict]:
        players = []
        table = soup.find("table", class_="tablesort")  # Таблица участников
        rows = table.find("tbody").find_all("tr")  # Все строки участников

        for row in rows:
            cells = row.find_all("td")
            if len(cells) > 0:  # Проверка наличия данных
                player_link = (
                    cells[1].find("a")["href"] if cells[1].find("a") else None
                )
                player_data = {
                    "rank": cells[0].text.strip(),
                    "name": cells[1].text.strip(),
                    "rating": cells[2].text.strip()
                    if cells[2].find("dfn")
                    else "нет",
                    "registration_date": cells[3].text.strip(),
                    "profile_link": cls.base_url + player_link
                    if player_link
                    else None,
                }
                players.append(player_data)
        return players

    @classmethod
    def _parse_withdrawn_players(cls, soup: BeautifulSoup) -> List[Dict]:
        withdrawn_players = []
        # Таблица снявшихся участников (изначально скрыта, имеет класс 'hide')
        table = soup.find("table", class_="tablesort hide")
        if table:  # Проверка на наличие таблицы снявшихся
            rows = table.find("tbody").find_all("tr")

            for row in rows:
                cells = row.find_all("td")
                if len(cells) > 0:  # Проверка наличия данных
                    player_link = (
                        cells[1].find("a")["href"]
                        if cells[1].find("a")
                        else None
                    )
                    withdrawn_player_data = {
                        "rank": cells[0].text.strip(),
                        "name": cells[1].text.strip(),
                        "rating": cells[2].text.strip()
                        if cells[2].find("dfn")
                        else "нет",
                        "withdrawal_date": cells[3].text.strip(),
                        "profile_link": cls.base_url + player_link
                        if player_link
                        else None,
                    }
                    withdrawn_players.append(withdrawn_player_data)

        return withdrawn_players


def main():
    with open("htmls/tournament/old.html", "r") as f:
        page = f.read()
    parse_result = TournamentParser().parse_data(page)
    print("\n".join(map(str, parse_result)))


if __name__ == "__main__":
    main()
