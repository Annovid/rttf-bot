import datetime

from clients.client import RTTFClient


def test_create_url_for_get_list_of_tournaments():
    url = RTTFClient().create_url_for_get_list_of_tournaments(
        date_from=datetime.date(2024, 11, 10),
        date_to=datetime.date(2024, 11, 12),
    )
    url_expected = (
        "https://m.rttf.ru/tournaments/"
        "?date_from=2024-11-10&date_to=2024-11-12&title=&search="
    )
    assert url == url_expected
