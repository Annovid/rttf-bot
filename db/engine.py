from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from utils.settings import settings


class SingletonEngine:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.engine = create_engine(*args, **kwargs)
        return cls._instance

    def get_engine(self):
        return self.engine


class SessionFactory:
    def __init__(self):
        self.engine = SingletonEngine(settings.DB_URL).get_engine()
        self.Session = sessionmaker(bind=self.engine)

    def __enter__(self):
        self.session = self.Session()
        return self.session

    def __exit__(self, exc_type, exc_value, traceback):
        self.session.commit()
        self.session.close()
