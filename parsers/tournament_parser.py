import re

from bs4 import BeautifulSoup

from parsers.parser import Parser
from utils.models import Player, PlayerResult, Tournament


class TournamentParser(Parser):
    @classmethod
    def _parse_data(cls, page: str) -> Tournament:
        soup = BeautifulSoup(page, 'html.parser')

        tournament_info = soup.find('h1')
        time_element = tournament_info.find('time')
        date_time = time_element.text.strip()  # Извлечение даты и времени
        tournament_name = tournament_info.text.replace(
            date_time, ''
        ).strip()  # Извлечение названия турнира
        tournament_location = tournament_info.find(
            'var'
        ).text.strip()  # Извлечение места

        # Извлечение идентификатора турнира
        tournament_link = soup.find('a', href=True, rel='nofollow')
        tournament_id = int(tournament_link['href'].split('%2F')[-1])  # Получение
        # идентификатора из ссылки

        registered_players = cls._parse_registered_players(soup)
        refused_players = cls._parse_withdrawn_players(soup)

        is_completed = cls._is_completed(soup)
        player_results = []
        if is_completed:
            player_results = cls._parse_player_results(soup)

        return Tournament(
            id=tournament_id,
            name=f'{tournament_name} ({date_time}, {tournament_location})',
            is_completed=is_completed,
            registered_players=registered_players,
            refused_players=refused_players,
            player_results=player_results,
        )

    @classmethod
    def _is_completed(cls, soup: BeautifulSoup) -> bool:
        table_completted = soup.find('table', class_='tablesort tour-players')
        if table_completted:
            return True
        return False

    @classmethod
    def _parse_registered_players(cls, soup: BeautifulSoup) -> list[Player]:
        players = []
        table_completted = soup.find('table', class_='tablesort tour-players')
        table = (
            table_completted
            if table_completted
            else soup.find('table', class_='tablesort')
        )
        if table is None:
            return []
        tbody = table.find('tbody')
        if tbody is None:
            return []
        rows = tbody.find_all('tr')  # Все строки участников
        for row in rows:
            cells = row.find_all('td')
            if len(cells) > 0:  # Проверка наличия данных
                player_link = cells[1].find('a')['href'] if cells[1].find('a') else None
                player = Player(
                    id=int(player_link.split('/')[-1].split('?')[0]),
                    name=cells[1].text.strip(),
                )
                players.append(player)
        return players

    # Эта функция во многом дублирует parse_registered_players
    # Отличия в структуре данных, включающей результаты
    # В будущем нужно перейти на нее
    @classmethod
    def _parse_player_results(cls, soup: BeautifulSoup) -> list[PlayerResult]:
        player_results = []
        table = soup.find('table', class_='tablesort tour-players')
        if not table:
            return player_results

        tbody = table.find('tbody')
        if tbody is None:
            return []
        rows = tbody.find_all('tr')  # Все строки участников
        for row in rows:
            cells = row.find_all('td')
            if len(cells) > 0:  # Проверка наличия данных
                player_link = cells[1].find('a')['href'] if cells[1].find('a') else None
                if not player_link:
                    continue
                name = cells[1].text.strip()
                player_id = int(player_link.split('/')[-1].split('?')[0])
                rating_before = float(cells[2].text.strip())
                rating_delta = float(cells[3].text.strip().replace('−', '-'))
                rating_after = float(cells[4].text.strip())
                games_str = cells[5].text.strip()
                _, games_won, games_lost = list(map(int, re.findall(r'\d+', games_str)))
                player_result = PlayerResult(
                    player_id=player_id,
                    name=name,
                    rating_before=rating_before,
                    rating_delta=rating_delta,
                    rating_after=rating_after,
                    games_won=games_won,
                    games_lost=games_lost,
                )
                player_results.append(player_result)
        return player_results

    @classmethod
    def _parse_withdrawn_players(cls, soup: BeautifulSoup) -> list[Player]:
        withdrawn_players = []
        # Таблица снявшихся участников (изначально скрыта, имеет класс 'hide')
        table = soup.find('table', class_='tablesort hide')
        if table is None:
            return []
        tbody = table.find('tbody')
        if tbody is None:
            return []
        rows = table.find('tbody').find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            if len(cells) > 0:  # Проверка наличия данных
                player_link = cells[1].find('a')['href'] if cells[1].find('a') else None
                player = Player(
                    id=int(player_link.split('/')[-1]),
                    name=cells[1].text.strip(),
                )
                withdrawn_players.append(player)

        return withdrawn_players


def main():
    with open('htmls/2024-11-02/current_pait.html', 'r') as f:
        page = f.read()
    parse_result = TournamentParser().parse_data(page)
    if not parse_result:
        raise Exception('Failed to parse tournament page')
    print(parse_result)
    print(parse_result.to_md())


if __name__ == '__main__':
    main()
