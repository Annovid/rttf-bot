from bs4 import BeautifulSoup

from parsers.parser import Parser
from utils.models import Player


class PlayersParser(Parser):
    @classmethod
    def _parse_data(cls, page: str) -> list[Player]:
        soup = BeautifulSoup(page, 'html.parser')
        players_data = []

        # Находим таблицу с игроками
        table_rows = soup.select('section.players-list tr')

        # Пропускаем заголовок таблицы и начинаем со строк с данными
        for row in table_rows[1:]:
            cells = row.find_all('td')
            if len(cells) < 4:
                continue  # Пропускаем некорректные строки

            # Извлечение данных из ячеек
            rank = cells[0].text.strip()  # Рейтинг
            name = cells[1].text.strip()  # Имя
            player_id = int(cells[1].find('a')['href'].split('/')[-1])
            city = cells[2].text.strip()  # Город
            rating = cells[3].find('dfn').text.strip()  # Рейтинг игрока

            player = Player(
                id=player_id,
                name=name,
                city=city,
                rating=rating,
            )

            players_data.append(player)

        return players_data


def main():
    with open('htmls/2024-10-26/players/3.html', 'r') as f:
        page = f.read()
    parse_result = PlayersParser()._parse_data(page)
    print('\n'.join(map(str, parse_result)))
    # {'rank': '40909', 'name': 'Синяев Нил', 'profile_link': 'https://m.rttf.ru/players/168970', 'city': 'Москва', 'rating': '206'}


if __name__ == '__main__':
    main()
