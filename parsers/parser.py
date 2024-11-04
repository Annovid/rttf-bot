import logging
from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from utils.custom_logger import custom_logger

T = TypeVar('T')


class Parser(ABC, Generic[T]):
    base_url = "https://m.rttf.ru/"

    @classmethod
    def parse_data(cls, page: str) -> T | None:
        try:
            parse_result = cls._parse_data(page)
            parse_result_str = str(parse_result)
            parse_result_representation = (
                parse_result_str if len(parse_result_str) < 100
                else parse_result_str[:100] + "..."
            )
            custom_logger.debug(f'Parse data succeeded: {parse_result_representation}')
            return parse_result
        except Exception as e:
            logging.error(f"Error while parsing page: {e}")
            return None

    @classmethod
    @abstractmethod
    def _parse_data(cls, page: str) -> T:
        pass
