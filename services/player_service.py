import datetime
import json

from clients.client import RTTFClient
from db.models import Tournament
from db.session_factory import open_session
from parsers.tournaments_parser import TournamentParseResult, TournamentsParser
from utils.custom_logger import logger
from utils.models import DateRange


class PlayerService:
    """
    Нужен, чтобы следить за активностью игроков

    Выполняет два основных сценария
    
    - Обновление списка существующих турниров
    - Обновление данных по игрокам по конкретному турниру
    """

    # Уносим парсинг в отдельную функцию, чтобы переопределять в тестах
    def _get_pages(self):
        pages = RTTFClient().get_tournaments_pages(
            date_range=DateRange(
                datetime.date.today() - datetime.timedelta(days=2),
                datetime.date.today() + datetime.timedelta(days=3)
            ),
        )
        return pages

    def update_tournaments(self):
        pages = self._get_pages()
        tournaments_data: list[TournamentParseResult] = []
        for page in pages:
            tournaments_data.extend(TournamentsParser.parse_data(page))
            
        added_list: list[TournamentParseResult] = []
        with open_session() as session:
            for tournament_parse in tournaments_data:
                existing = session.query(Tournament).filter_by(id=tournament_parse.id).first()
                if not existing:
                    # inserting new tournament record
                    tournament_info = {
                        'name': tournament_parse.name,
                        'rating': tournament_parse.rating,
                    }
                    dt = datetime.datetime.strptime(tournament_parse.datetime, "%Y-%m-%d %H:%M")
                    tournament_date = dt.date()
                    tournament_record = Tournament(
                        id=tournament_parse.id,
                        tournament_date=tournament_date,
                        info_json=json.dumps(tournament_info),
                        # datetime.now приводит к скорейшей обработке турнира
                        # другим кроном
                        next_update_dtm=datetime.datetime.now().timestamp(),
                    )
                    session.add(tournament_record)
                    added_list.append(tournament_parse)
            session.commit()
        for added in added_list:
            logger.info(f'Added tournament {str(added)}')
        return added_list
    