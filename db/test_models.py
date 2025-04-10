import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from alembic import command
from alembic.config import Config
from db.models import Base, DBUserConfig, Player, Tournament, Subscription, PlayerTournament
from utils.models import UserConfig

from utils.settings import settings
from datetime import date

# Create a new SQLite database for testing
TEST_DATABASE_URL = "sqlite:///:memory:"
settings.DB_URL = TEST_DATABASE_URL
engine = create_engine(TEST_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope='module')
def test_db():
    # Apply Alembic migrations
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.attributes['connection'] = engine
    command.upgrade(alembic_cfg, "head")
    
    session = SessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

def test_db_user_config(test_db):
    user_config = UserConfig(id=1, username="123")
    
    DBUserConfig.save_config(user_config, test_db)
    # Save the user config
    
    # Retrieve the user config
    retrieved_config = DBUserConfig.get_by_id(test_db, user_config.id)
    assert retrieved_config is not None
    assert retrieved_config.config == user_config.to_dict()

def test_player_model(test_db):
    player = Player(id=1, name="Test Player")
    test_db.add(player)
    test_db.commit()
    
    retrieved_player = test_db.query(Player).filter_by(id=1).first()
    assert retrieved_player is not None
    assert retrieved_player.name == "Test Player"

def test_tournament_model(test_db):
    tournament = Tournament(id=1, tournament_date=date(2023, 10, 26), info_json='{}')
    test_db.add(tournament)
    test_db.commit()
    
    retrieved_tournament = test_db.query(Tournament).filter_by(id=1).first()
    assert retrieved_tournament is not None
    assert retrieved_tournament.tournament_date == date(2023, 10, 26)

def test_subscription_model(test_db):
    user_config = UserConfig(id=2, username="123")
    db_user_config = DBUserConfig(id=user_config.id, config=user_config.to_dict())
    db_user_config.save_config(user_config, test_db)

    player = Player(id=2, name="Test Player")
    test_db.add(player)
    test_db.commit()

    subscription = Subscription(user_id=user_config.id, player_id=player.id)
    test_db.add(subscription)
    test_db.commit()

    retrieved_subscription = test_db.query(Subscription).filter_by(user_id=user_config.id, player_id=player.id).first()
    assert retrieved_subscription is not None

def test_player_tournament_model(test_db):
    player = Player(id=3, name="Test Player")
    tournament = Tournament(id=2, tournament_date=date(2023, 10, 26), info_json='{}')
    test_db.add(player)
    test_db.add(tournament)
    test_db.commit()

    player_tournament = PlayerTournament(player_id=player.id, tournament_id=tournament.id, results_json='{}')
    test_db.add(player_tournament)
    test_db.commit()

    retrieved_player_tournament = test_db.query(PlayerTournament).filter_by(player_id=player.id, tournament_id=tournament.id).first()
    assert retrieved_player_tournament is not None
