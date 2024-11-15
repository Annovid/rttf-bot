import logging
import os
from datetime import datetime


class CustomLogger:
    @staticmethod
    def setup_logger() -> logging.Logger:
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        log_filename = datetime.now().strftime("%H-%M-%S.log")
        log_filepath = os.path.join(log_dir, log_filename)

        logger = logging.getLogger("custom_logger")
        logger.setLevel(logging.DEBUG)
        file_handler = logging.FileHandler(log_filepath, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        logger.info("Logger setup")
        return logger


custom_logger: logging.Logger = CustomLogger.setup_logger()


def main():
    custom_logger.debug("This is a debug message.")
    custom_logger.info("This is an info message.")
    custom_logger.warning("This is a warning message.")
    custom_logger.error("This is an error message.")
    try:
        1 / 0
    except ZeroDivisionError:
        custom_logger.exception("An exception occurred")


if __name__ == "__main__":
    main()
