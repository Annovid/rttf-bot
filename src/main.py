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
    parser.add_argument('--process-tournaments-batch', action='store_true', help='Process tournaments batch using process_batch_and_notify with batch size 10')
    args = parser.parse_args()

    if args.parse_tournaments:
        player_service = PlayerService()
        tournaments_data = player_service.update_tournaments()
        logger.info('\n'.join(map(str, tournaments_data)))
    elif args.process_tournaments_batch:
        player_service = PlayerService()
        updates = player_service.process_batch_and_notify(batch_size=25)
        logger.info(updates)
    else:
        logger.info('Bot started')
        bot_context.bot.infinity_polling(
            # timeout=10,
            # long_polling_timeout=5,
        )
        logger.info('Bot finished')


if __name__ == '__main__':
    main()
