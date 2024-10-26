from bs4 import BeautifulSoup

from parsers.parser import Parser


class PlayerParser(Parser):
    @classmethod
    def _parse_data(cls, page: str):
        soup = BeautifulSoup(page, "html.parser")
        # Парсинг имени и ID игрока
        player_section = soup.find("section", class_="player-info")
        player_name = player_section.find("h1").text.strip()
        rating = player_section.find("h3").find("dfn").text.strip()
        player_nickname = player_section.find("h3").contents[0].strip()

        elements = soup.find_all("p")
        add_dict = {}
        for element in elements:
            if element.text.startswith("город"):
                add_dict["city"] = element.find("strong").text
            if element.text.startswith("Игровая рука"):
                add_dict["hand"] = element.find("strong").text

        player_data = {
            "nickname": player_nickname,
            "player_id": rating,
            "name": player_name,
            **add_dict,
        }

        return player_data


def main():
    with open("htmls/player/annovid.html", "r") as f:
        page = f.read()
    parse_result = PlayerParser()._parse_data(page)
    print(parse_result)
    # {'nickname': 'Annovid', 'player_id': '201', 'name': 'Синяев Нил Викторович', 'city': 'Москва', 'hand': 'левая'}


if __name__ == "__main__":
    main()
