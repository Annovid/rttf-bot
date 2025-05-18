import os.path
import datetime
import random
import time
from multiprocessing.pool import ThreadPool
from typing import Any

import requests
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

from utils.models import DateRange
from utils.settings import settings
from utils.custom_logger import logger

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:112.0) Gecko/20100101 Firefox/112.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, "
    "like Gecko) Chrome/110.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/113.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 ("
    "KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
]


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
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_fixed(2),
        retry=retry_if_exception_type((requests.RequestException, RuntimeError)),
    )
    def make_request(
            cls,
            url: str,
            headers: dict[str, Any] | None = None,
            raise_404: bool = True,
    ) -> requests.Response:
        if headers is None:
            headers = cls.headers.copy()
        headers["User-Agent"] = random.choice(USER_AGENTS)

        try:
            response = requests.get(url=url, headers=headers)
            if not raise_404 and response.status_code == 404:
                logger.debug('Page not found %s', url)
                return response
            response.raise_for_status()
            logger.debug('Successful request to %s', url)
            return response
        except requests.RequestException as e:
            logger.warning('Failed request to %s', url)
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
    def create_url_for_get_tournaments_pages(
            cls,
            date_range: DateRange | None = None,
            only_moscow: bool = True,
    ) -> str:
        if date_range is None and only_moscow:
            return 'https://m.rttf.ru/tournaments/?cities[]=r77'
        if date_range is None and not only_moscow:
            raise NotImplementedError('Bad params')
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
        url = cls.create_url_for_get_tournaments_pages(
            date_range=DateRange(single_date, single_date)
        )
        response = cls.make_request(url)
        return response.text

    @classmethod
    def get_tournaments_pages(
            cls,
            date_range: DateRange | None = None,
    ) -> list[str]:
        if date_range is None:
            date_range = DateRange()
        dates = [
            date_range.date_from + datetime.timedelta(days=i)
            for i in range((date_range.date_to - date_range.date_from).days + 1)
        ]
        with ThreadPool(settings.MAX_WORKERS) as pool:
            pages = pool.map(cls.get_tournaments_for_date, dates)
        date_page_mapping = list(zip(dates, pages))
        return [page for date, page in date_page_mapping]

    @classmethod
    def get_tournament(
            cls,
            tournament_id: int,
    ) -> str:
        url = os.path.join(cls.BASE_URL, 'tournaments', str(tournament_id))
        response = cls.make_request(url, raise_404=False)
        if response.status_code != 404:
            logger.info('Downloaded tournament {}'.format(tournament_id))
            return response.text
        return ''

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
