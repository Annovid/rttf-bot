import logging
from abc import ABC, abstractmethod


class Parser(ABC):
    base_url = "https://m.rttf.ru/"

    @classmethod
    def parse_data(cls, page: str):
        try:
            return cls._parse_data(page)
        except Exception as e:
            logging.error(f"Error while parsing page: {e}")
            return None

    @classmethod
    @abstractmethod
    def _parse_data(cls, page: str):
        pass
