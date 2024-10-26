import logging
import os.path
import urllib.parse
import datetime
from typing import Any

import requests


class RTTFClient:
    base_url = "https://m.rttf.ru/"
    cities = ["r77"]
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/58.0.3029.110 Safari/537.3"
        )
    }

    @classmethod
    def make_request(
        cls,
        url: str,
        headers: dict[str, Any] | None = None,
    ) -> requests.Response:
        if headers is None:
            headers = cls.headers
        try:
            response = requests.get(url=url, headers=headers)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            raise RuntimeError(f"Error during request: {e}")

    @classmethod
    def create_url_for_get_list_of_tournaments(
        cls,
        date_from: datetime.date,
        date_to: datetime.date,
        title: str = "",
    ) -> str:
        query_params = {
            "date_from": date_from.strftime("%Y-%m-%d"),
            "date_to": date_to.strftime("%Y-%m-%d"),
            "title": title,
        }
        tournaments_url = os.path.join(cls.base_url, "tournaments")
        url_parts = list(urllib.parse.urlparse(tournaments_url))
        url_parts[4] = urllib.parse.urlencode(query_params, doseq=True)
        return str(urllib.parse.urlunparse(url_parts))

    @classmethod
    def get_list_of_tournaments(
        cls,
        date_from: datetime.date,
        date_to: datetime.date,
        title: str = "",
    ) -> str:
        url = cls.create_url_for_get_list_of_tournaments(
            date_from, date_to, title
        )
        response = cls.make_request(url)
        logging.info("Downloaded tournaments")
        return response.text

    @classmethod
    def get_tournament(
        cls,
        tournament_id: int,
    ) -> str:
        url = os.path.join(cls.base_url, "tournaments", str(tournament_id))
        response = cls.make_request(url)
        logging.info("Downloaded tournament {}".format(tournament_id))
        return response.text

    @classmethod
    def get_player(cls, player_id: int) -> str:
        url = os.path.join(cls.base_url, "players", str(player_id))
        response = cls.make_request(url)
        logging.info("Downloaded player {}".format(player_id))
        return response.text

    @classmethod
    def get_players(cls, search_str: str) -> str:
        url = os.path.join(cls.base_url, "players") + "/?name=" + search_str
        response = cls.make_request(url)
        logging.info(
            "Downloaded players search with str {}".format(search_str)
        )
        return response.text


def main():
    page = RTTFClient.get_player(168970)
    with open("htmls/player/annovid.html", "w") as f:
        f.write(page)
    print(len(page))


if __name__ == "__main__":
    main()
