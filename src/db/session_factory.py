from collections.abc import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager

from utils.settings import settings

engine = create_engine(settings.DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextmanager
def open_session() -> Generator[Session, None, None]:
    """
    Создает новую сессию для взаимодействия с базой данных.
    Автоматически закрывает сессию по завершении контекста.
    """
    session = SessionLocal()
    try:
        yield session  # Возвращаем сессию
        session.commit()  # Автоматически коммитит изменения
    except Exception:
        session.rollback()  # Откатывает изменения при ошибке
        raise
    finally:
        session.close()  # Закрываем сессию
