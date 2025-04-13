from bot.bot_setup import bot_context
from utils.custom_logger import logger


def main():
    logger.info('Bot started')
    bot_context.bot.infinity_polling(
        # timeout=10,
        # long_polling_timeout=5,
    )
    logger.info('Bot finished')


if __name__ == '__main__':
    main()
