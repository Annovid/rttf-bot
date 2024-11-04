from bs4 import BeautifulSoup

from parsers.parser import Parser
from utils.models import Tournament, Player


class TournamentParser(Parser):
    @classmethod
    def _parse_data(cls, page: str) -> Tournament:
        soup = BeautifulSoup(page, "html.parser")

        tournament_info = soup.find("h1")
        time_element = tournament_info.find("time")
        date_time = time_element.text.strip()  # Извлечение даты и времени
        tournament_name = tournament_info.text.replace(date_time, '').strip()  # Извлечение названия турнира
        tournament_location = tournament_info.find("var").text.strip()  # Извлечение места

        # Извлечение идентификатора турнира
        tournament_link = soup.find("a", href=True, rel="nofollow")
        tournament_id = int(tournament_link['href'].split('%2F')[-1])  # Получение
        # идентификатора из ссылки

        registered_player_ids = cls._parse_registered_players(soup)
        refused_player_ids = cls._parse_withdrawn_players(soup)

        return Tournament(
            id=tournament_id,
            name=f"{tournament_name} ({date_time}, {tournament_location})",
            registered_players=registered_player_ids,
            refused_players=refused_player_ids,
        )
    @classmethod
    def _parse_registered_players(cls, soup: BeautifulSoup) -> list[Player]:
        players = []
        table = soup.find("table", class_="tablesort")  # Таблица участников
        if table is None:
            return []
        tbody = table.find("tbody")
        if tbody is None:
            return []
        rows = tbody.find_all("tr")  # Все строки участников
        for row in rows:
            cells = row.find_all("td")
            if len(cells) > 0:  # Проверка наличия данных
                player_link = (
                    cells[1].find("a")["href"] if cells[1].find("a") else None
                )
                player = Player(
                    id=int(player_link.split('/')[-1].split('?')[0]),
                    name=cells[1].text.strip(),
                )
                players.append(player)
        return players

    @classmethod
    def _parse_withdrawn_players(cls, soup: BeautifulSoup) -> list[Player]:
        withdrawn_players = []
        # Таблица снявшихся участников (изначально скрыта, имеет класс 'hide')
        table = soup.find("table", class_="tablesort hide")
        if table is None:
            return []
        tbody = table.find("tbody")
        if tbody is None:
            return []
        rows = table.find("tbody").find_all("tr")
        for row in rows:
            cells = row.find_all("td")
            if len(cells) > 0:  # Проверка наличия данных
                player_link = (
                    cells[1].find("a")["href"] if cells[1].find("a") else None
                )
                player = Player(
                    id=int(player_link.split('/')[-1]),
                    name=cells[1].text.strip(),
                )
                withdrawn_players.append(player)

        return withdrawn_players


def main():
    with open("resources/temp.html", "r") as f:
        page = f.read()
    parse_result = TournamentParser()._parse_data(page)
    print(parse_result)
    print(parse_result.to_md())


if __name__ == "__main__":
    main()
