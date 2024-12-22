import os.path
import datetime
from multiprocessing.pool import ThreadPool
from typing import Any

import requests

from utils.models import DateRange
from utils.settings import settings
from utils.custom_logger import logger


class RTTFClient:
    BASE_URL = 'https://m.rttf.ru/'
    cities = ['r77']
    headers = {
        'User-Agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/58.0.3029.110 Safari/537.3'
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
            raise RuntimeError(f'Error during request: {e}')

    @classmethod
    def make_request_all_data(
        cls, url: str, headers: dict[str, Any] | None = None
    ) -> list:
        if headers is None:
            headers = cls.headers

        all_data = []

        while url:  # Continue until no further page
            try:
                response = requests.get(url=url, headers=headers)
                response.raise_for_status()
                data = response.json()  # Assumes JSON response

                all_data.extend(data['results'])  # Append page data

                # Update `url` for the next page
                url = data.get('next')
            except requests.RequestException as e:
                raise RuntimeError(f'Error during request: {e}')
        return all_data

    @classmethod
    def create_url_for_get_list_of_tournaments(
        cls,
        date_range: DateRange | None = None,
        only_moscow: bool = True,
    ) -> str:
        if date_range is None and only_moscow:
            return f'https://m.rttf.ru/tournaments/?cities[]=r77'
        if date_range is None and not only_moscow:
            raise NotImplemented('Bad params')
        msc_substr = '&cities%5B%5D=r77' if only_moscow else ''
        return (
            f'https://m.rttf.ru/tournaments/'
            f'?date_from={date_range.date_from}'
            f'&date_to={date_range.date_to}'
            f'&title='
            f'{msc_substr}'
            f'&search='
        )

    @classmethod
    def get_tournaments_for_date(cls, single_date: datetime.date | None = None) -> str:
        """Скачивает html с турнирами.

        Если single_date указана, скачивает для данной даты, иначе скачивает для
        стартовой страницы.
        Не реализован метод скачивания для диапазона дат, так как не понятно, как
        обойти пагинацию.
        """
        url = cls.create_url_for_get_list_of_tournaments(
            date_range=DateRange(single_date, single_date)
        )
        response = cls.make_request(url)
        return response.text

    @classmethod
    def get_list_of_tournaments(
        cls,
        date_range: DateRange = DateRange,
    ) -> list[str]:
        date_range = [
            date_range.date_from + datetime.timedelta(days=n)
            for n in range((date_range.date_to - date_range.date_from).days + 1)
        ]
        with ThreadPool(settings.MAX_WORKERS) as pool:
            pages = pool.map(cls.get_tournaments_for_date, date_range)
        for date, result in zip(date_range, pages):
            logger.info(f'Downloaded tournaments for {date}')
        return [page for date, page in zip(date_range, pages)]

    @classmethod
    def get_tournament(
        cls,
        tournament_id: int,
    ) -> str:
        url = os.path.join(cls.BASE_URL, 'tournaments', str(tournament_id))
        response = cls.make_request(url)
        logger.info('Downloaded tournament {}'.format(tournament_id))
        return response.text

    @classmethod
    def get_player(cls, player_id: int) -> str:
        url = os.path.join(cls.BASE_URL, 'players', str(player_id))
        response = cls.make_request(url)
        logger.info('Downloaded player {}'.format(player_id))
        return response.text

    @classmethod
    def get_players(cls, search_str: str) -> str:
        url = os.path.join(cls.BASE_URL, 'players') + '/?name=' + search_str
        response = cls.make_request(url)
        logger.info('Downloaded players search with str {}'.format(search_str))
        return response.text


def main():
    page = RTTFClient.get_player(168970)
    with open('htmls/player/annovid.html', 'w') as f:
        f.write(page)
    print(len(page))


if __name__ == '__main__':
    main()
