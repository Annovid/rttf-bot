import logging
import urllib.parse
import datetime
from typing import Optional, Any

import requests
from gyp.generator.make import header


class RTTFClient:
    base_url = "https://m.rttf.ru/tournaments/"
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
        url_parts = list(urllib.parse.urlparse(cls.base_url))
        url_parts[4] = urllib.parse.urlencode(query_params, doseq=True)
        return str(urllib.parse.urlunparse(url_parts))

    @classmethod
    def create_url_for_get_tournament(
        cls,
        tournament_id: int,
    ) -> str:
        return f"{cls.base_url}{tournament_id}"

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
        url = cls.create_url_for_get_tournament(tournament_id)
        response = cls.make_request(url)
        logging.info("Downloaded tournament {}".format(tournament_id))
        return response.text


def main():
    page = RTTFClient.get_tournament(143649)
    with open("htmls/tournament/new2.html", "w") as f:
        f.write(page)
    print(len(page))


if __name__ == "__main__":
    main()
