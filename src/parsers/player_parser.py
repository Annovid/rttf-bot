from bs4 import BeautifulSoup

from parsers.parser import Parser
from utils.models import Player


class PlayerParser(Parser):
    @classmethod
    def _parse_data(cls, page: str) -> Player:
        soup = BeautifulSoup(page, 'html.parser')

        # Парсинг ID игрока
        player_id = None
        elements = soup.find_all('a')
        for element in elements:
            if element.get_text() == 'Профиль':
                player_id = int(element.get('href').split('/')[-1])
        if not player_id:
            raise Exception('Player id not found')

        # Парсинг имени и рейтинга игрока
        player_section = soup.find('section', class_='player-info')
        player_name = player_section.find('h1').text.strip()
        rating = player_section.find('h3').find('dfn').text.strip()
        try:
            player_nickname = player_section.find('h3').contents[0].strip()
        except TypeError:
            player_nickname = None

        elements = soup.find_all('p')
        add_dict = {}
        for element in elements:
            if element.text.startswith('город'):
                add_dict['city'] = element.find('strong').text
            if element.text.startswith('Игровая рука'):
                add_dict['hand'] = element.find('strong').text

        player_data = {
            'id': player_id,
            'nickname': player_nickname,
            'rating': rating,
            'name': player_name,
            **add_dict,
        }

        return Player(**player_data)


def main():
    with open('htmls/player/annovid.html', 'r') as f:
        page = f.read()
    parse_result = PlayerParser()._parse_data(page)
    print(parse_result)
    print(parse_result.to_md())
    print(parse_result.to_md2())
    print(parse_result.to_md_one_str())


if __name__ == '__main__':
    main()
