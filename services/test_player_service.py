import os
from collections import namedtuple

import pytest
import sqlalchemy as sa

import utils.settings as settings_mod
from db.models import Base, Tournament
from db.session_factory import SessionLocal
from services.player_service import PlayerService

# Override DB settings for testing (using in-memory SQLite)
TEST_DATABASE_URL = 'sqlite:///:memory:'

settings_mod.settings.DB_URL = TEST_DATABASE_URL


@pytest.fixture(scope='module')
def setup_db():
    engine = sa.create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(engine)
    # Reconfigure SessionLocal to use the test engine
    SessionLocal.configure(bind=engine)
    yield
    engine.dispose()


class PlayerServiceNotFull(PlayerService):
    """Парсит страницу, где не часть турниров удалено"""

    def _get_pages(self):
        pages = []
        path = 'htmls/2025-04-12/tournaments/not_full_list.html'
        if os.path.isfile(path):
            with open(path, 'r', encoding='utf-8') as f:
                pages.append(f.read())
        return pages


class PlayerServiceFull(PlayerService):
    """Парсит полную страницу с турнирами"""

    def _get_pages(self):
        pages = []
        path = 'htmls/2025-04-12/tournaments/full_list.html'
        if os.path.isfile(path):
            with open(path, 'r', encoding='utf-8') as f:
                pages.append(f.read())
        return pages


def test_update_tournaments(setup_db):
    # База пустая, ожидаем, что все турниры попадут в базу
    service = PlayerServiceNotFull()
    service.update_tournaments()
    with SessionLocal() as session:
        count = session.query(Tournament).count()
    assert count == 48, f'Expected 48 tournaments after first update, got {count}'

    # В полном списке на 3 турнира больше. Ожидаем, что в базу попадут только они
    service = PlayerServiceFull()
    service.update_tournaments()
    with SessionLocal() as session:
        count = session.query(Tournament).count()
    assert count == 51, f'Expected 51 tournaments after second update, got {count}'
