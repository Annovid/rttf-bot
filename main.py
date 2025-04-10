import sys
import argparse
import datetime
from bot.bot_setup import bot_context
from utils.custom_logger import logger
from clients.client import RTTFClient
from parsers.tournaments_parser import TournamentsParser
from utils.models import DateRange


def parse_tournaments():
    pages = RTTFClient().get_tournaments_pages(
        date_range=DateRange(
            datetime.date.today() - datetime.timedelta(days=2),
            datetime.date.today() + datetime.timedelta(days=3)
        ),
    )
    tournaments_data = []
    for page in pages:
        tournaments_data.extend(TournamentsParser.parse_data(page))
    print('\n'.join(map(str, tournaments_data)))


def main():
    parser = argparse.ArgumentParser(description='Tournament Parser')
    parser.add_argument('--parse-tournaments', action='store_true', help='Parse tournaments from two days before to three days after today')
    args = parser.parse_args()

    if args.parse_tournaments:
        parse_tournaments()
    else:
        logger.info('Bot started')
        bot_context.bot.infinity_polling(
            # timeout=10,
            # long_polling_timeout=5,
        )
        logger.info('Bot finished')


if __name__ == '__main__':
    main()
