from datetime import date, datetime

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.models import (
    Base,
    DBPlayerTournament,
    DBSubscription,
    DBTournament,
    DBUserConfig,
)
from utils.models import UserConfig
from utils.settings import settings

# Create a new SQLite database for testing
TEST_DATABASE_URL = 'sqlite:///:memory:'
settings.DB_URL = TEST_DATABASE_URL
engine = create_engine(TEST_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope='module')
def test_db():
    # Apply Alembic migrations
    alembic_cfg = Config('alembic.ini')
    alembic_cfg.attributes['connection'] = engine
    command.upgrade(alembic_cfg, 'head')

    session = SessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


def test_db_user_config(test_db):
    user_config = UserConfig(id=1, username='123')

    DBUserConfig.save_config(user_config, test_db)
    # Save the user config

    # Retrieve the user config
    retrieved_config = DBUserConfig.get_by_id(test_db, user_config.id)
    assert retrieved_config is not None
    assert retrieved_config.config == user_config.to_dict()


def test_tournament_model(test_db):
    # Create tournament with id 1 and set players [1, 2, 3] using our custom storage format.
    tournament1 = DBTournament(id=1, tournament_date=date(2023, 10, 26), info_json='{}')
    tournament1.set_players([1, 2, 3])
    test_db.add(tournament1)
    test_db.commit()

    # Create a second tournament without players.
    tournament2 = DBTournament(id=2, tournament_date=date(2023, 10, 26), info_json='{}')
    test_db.add(tournament2)
    test_db.commit()

    # retrieve tournament with id 1 and verify its data.
    retrieved_tournament = test_db.query(DBTournament).filter_by(id=1).first()
    assert retrieved_tournament is not None
    assert retrieved_tournament.tournament_date == date(2023, 10, 26)

    # Query tournaments that contain the player id 2.
    # Here, we assume you defined a method/property on DBTournament, e.g. a hybrid method,
    # called `contains_player` that returns a SQL clause using LIKE.
    found = test_db.query(DBTournament).filter(DBTournament.contains_player(2)).all()
    assert len(found) == 1
    assert found[0].id == 1


def test_subscription_model(test_db):
    user_config = UserConfig(id=2, username='123')
    db_user_config = DBUserConfig(id=user_config.id, config=user_config.to_dict())
    db_user_config.save_config(user_config, test_db)

    subscription = DBSubscription(user_id=user_config.id, player_id=2)
    test_db.add(subscription)
    test_db.commit()

    retrieved_subscription = (
        test_db.query(DBSubscription)
        .filter_by(user_id=user_config.id, player_id=2)
        .first()
    )
    assert retrieved_subscription is not None


def test_player_tournament_model(test_db):
    tournament = DBTournament(id=3, tournament_date=date(2023, 10, 26), info_json='{}')
    test_db.add(tournament)
    test_db.commit()

    player_tournament = DBPlayerTournament(
        player_id=3, tournament_id=tournament.id, info_json='{}'
    )
    test_db.add(player_tournament)
    test_db.commit()

    retrieved_player_tournament = (
        test_db.query(DBPlayerTournament)
        .filter_by(player_id=3, tournament_id=tournament.id)
        .first()
    )
    assert retrieved_player_tournament is not None


def test_process_subs_diff_activate(test_db):
    # Subscription activation: false -> true, add all friends from new_config
    user_id = 10
    old_config = UserConfig(
        id=user_id, username='test', friend_ids={100, 101, 102}, subscription_on=False
    )
    new_config = UserConfig(
        id=user_id, username='test', friend_ids={100, 101, 102}, subscription_on=True
    )
    # Create a tournament that includes friend 100 so we can check update timestamp
    tournament = DBTournament(
        id=1000, tournament_date=date(2023, 10, 26), info_json='{}'
    )
    tournament.set_players([100])
    test_db.add(tournament)
    test_db.commit()
    now = datetime.now()
    DBSubscription.process_subs_diff(test_db, old_config, new_config, now=now)
    test_db.commit()
    subs = test_db.query(DBSubscription).filter_by(user_id=user_id).all()
    friend_ids = {sub.player_id for sub in subs}
    assert friend_ids == {100, 101, 102}
    tournament = test_db.query(DBTournament).filter_by(id=1000).first()
    assert tournament.next_update_dtm is not None
    assert abs(tournament.next_update_dtm - now.timestamp()) < 1.0


def test_process_subs_diff_deactivate(test_db):
    # Subscription deactivation: true -> false, remove all subscriptions
    user_id = 11
    # Pre-populate subscriptions for the user
    for fid in (200, 201):
        test_db.add(DBSubscription(user_id=user_id, player_id=fid))
    test_db.commit()
    old_config = UserConfig(
        id=user_id, username='test', friend_ids={200, 201}, subscription_on=True
    )
    new_config = UserConfig(
        id=user_id, username='test', friend_ids={200, 201}, subscription_on=False
    )
    DBSubscription.process_subs_diff(test_db, old_config, new_config)
    test_db.commit()
    subs = test_db.query(DBSubscription).filter_by(user_id=user_id).all()
    assert len(subs) == 0


def test_process_subs_diff_incremental(test_db):
    # Incremental update: subscription_on remains True, but friend_ids change
    user_id = 12
    old_config = UserConfig(
        id=user_id, username='test', friend_ids={300, 301, 302}, subscription_on=True
    )
    # Pre-populate subscriptions for old_config
    for fid in old_config.friend_ids:
        test_db.add(DBSubscription(user_id=user_id, player_id=fid))
    test_db.commit()
    # Create a tournament that includes the new friend 303
    tournament = DBTournament(
        id=1001, tournament_date=date(2023, 10, 26), info_json='{}'
    )
    tournament.set_players([303])
    test_db.add(tournament)
    test_db.commit()
    now = datetime.now()
    # New config: remove 300, add 303
    new_config = UserConfig(
        id=user_id, username='test', friend_ids={301, 302, 303}, subscription_on=True
    )
    DBSubscription.process_subs_diff(test_db, old_config, new_config, now=now)
    test_db.commit()
    subs = test_db.query(DBSubscription).filter_by(user_id=user_id).all()
    friend_ids = {sub.player_id for sub in subs}
    assert friend_ids == {301, 302, 303}
    tournament = test_db.query(DBTournament).filter_by(id=1001).first()
    assert tournament.next_update_dtm is not None
    assert abs(tournament.next_update_dtm - now.timestamp()) < 1.0
