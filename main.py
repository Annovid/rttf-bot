import sys
import argparse
import datetime
from bot.bot_setup import bot_context
from utils.custom_logger import logger
from clients.client import RTTFClient
from parsers.tournaments_parser import TournamentsParser
from utils.models import DateRange
from services.player_service import PlayerService


def main():
    parser = argparse.ArgumentParser(description='Tournament Parser')
    parser.add_argument('--parse-tournaments', action='store_true', help='Parse tournaments from two days before to three days after today')
    args = parser.parse_args()

    if args.parse_tournaments:
        player_service = PlayerService()
        tournaments_data = player_service.update_tournaments()
        print('\n'.join(map(str, tournaments_data)))
    else:
        logger.info('Bot started')
        bot_context.bot.infinity_polling(
            # timeout=10,
            # long_polling_timeout=5,
        )
        logger.info('Bot finished')


if __name__ == '__main__':
    main()
