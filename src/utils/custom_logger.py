import logging
import os
from datetime import datetime
import requests

from logging_loki import LokiHandler

from utils.settings import settings


class CustomLogger:
    @staticmethod
    def setup_logger() -> logging.Logger:
        logger = logging.getLogger('custom_logger')
        logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            fmt='%(asctime)s - %(levelname)-8s - %(message)s'
        )

        CustomLogger._add_file_handler(logger, formatter)
        CustomLogger._add_console_handler(logger, formatter)
        if getattr(settings, "USE_LOKI", False):
            CustomLogger._add_loki_handler(logger, formatter)

        logger.info('Logger setup complete')
        return logger

    @staticmethod
    def _add_file_handler(logger: logging.Logger, formatter: logging.Formatter):
        log_dir = 'logs'
        os.makedirs(log_dir, exist_ok=True)
        log_filename = datetime.now().strftime('%Y-%m-%d %H-%M-%S.log')
        log_filepath = os.path.join(log_dir, log_filename)

        file_handler = logging.FileHandler(log_filepath, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    @staticmethod
    def _add_console_handler(logger: logging.Logger, formatter: logging.Formatter):
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    @staticmethod
    def _add_loki_handler(logger: logging.Logger, formatter: logging.Formatter):
        try:
            loki_url = settings.LOKI_URL
            environment = settings.ENVIRONMENT

            check = requests.get(f"http://{loki_url}/ready", timeout=5)
            if check.status_code != 200:
                raise ConnectionError(f"Loki server not available (status {check.status_code})")

            loki_handler = LokiHandler(
                url=f"http://{loki_url}/loki/api/v1/push",
                tags={
                    "application": "rttf-bot",
                    "environment": environment,
                    "service": settings.SERVICE_NAME,
                },
                version="1",
            )
            loki_handler.setLevel(logging.DEBUG)
            loki_handler.setFormatter(formatter)
            logger.addHandler(loki_handler)
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to connect to Loki server: {e}")


logger: logging.Logger = CustomLogger.setup_logger()


def main():
    logger.debug('This is a debug message.')
    logger.info('This is an info message.')
    logger.warning('This is a warning message.')
    logger.error('This is an error message.')
    try:
        1 / 0
    except ZeroDivisionError:
        logger.exception('An exception occurred')


if __name__ == '__main__':
    main()
