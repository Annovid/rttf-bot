import datetime
import json
from collections import defaultdict
from typing import Optional

from bot.bot_context import bot_context
from bot.notifications import send_player_update
from clients.client import RTTFClient
from db.models import DBPlayerTournament, DBSubscription, DBTournament
from db.session_factory import open_session
from parsers.tournament_parser import TournamentParser
from parsers.tournaments_parser import TournamentParseResult, TournamentsParser
from utils.custom_logger import logger
from utils.models import DateRange, PlayerTournamentInfo, Tournament


class PlayerService:
    """
    Нужен, чтобы следить за активностью игроков

    Выполняет два основных сценария

    - Обновление списка существующих турниров
    - Обновление данных по игрокам по конкретному турниру
    """

    # Уносим парсинг и нотификации в отдельные методы, чтобы переопределять в тестах
    def _get_tournaments_pages(self):
        pages = RTTFClient().get_tournaments_pages(
            date_range=DateRange(
                datetime.date.today() - datetime.timedelta(days=2),
                datetime.date.today() + datetime.timedelta(days=3),
            ),
        )
        return pages

    def _get_tournament_page(self, tournament_id):
        page = RTTFClient().get_tournament(tournament_id)
        return page

    def _send_player_update(self, user_id, info):
        send_player_update(user_id, info, bot_context=bot_context)

    def update_tournaments(self):
        pages = self._get_tournaments_pages()
        tournaments_data: list[TournamentParseResult] = []
        for page in pages:
            tournaments_data.extend(TournamentsParser.parse_data(page))

        added_list: list[TournamentParseResult] = []
        with open_session() as session:
            for tournament_parse in tournaments_data:
                existing = (
                    session.query(DBTournament)
                    .filter_by(id=tournament_parse.id)
                    .first()
                )
                if not existing:
                    # inserting new tournament record
                    tournament_info = {
                        'name': tournament_parse.name,
                        'rating': tournament_parse.rating,
                    }
                    dt = datetime.datetime.strptime(
                        tournament_parse.datetime, '%Y-%m-%d %H:%M'
                    )
                    tournament_date = dt.date()
                    tournament_record = DBTournament(
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

    def _get_subscriptions_dict(self) -> dict[int, list[int]]:
        """Возвращает словарь игроков и кто на них подписан
        Формат: player_id -> list[user_id]
        """
        player_users = defaultdict(list)
        with open_session() as session:
            subscriptions = session.query(DBSubscription).all()
            for sub in subscriptions:
                player_users[sub.player_id].append(sub.user_id)
        return dict(player_users)

    def _update_player_tournaments(self, players, tournament_id):
        """Обновляет таблицу участий игроков в турнирах

        Returns:
        updated (dict): словарь с апдейтами, которые пойдут в нотификации
        is_ok (bool): False, если турнир не спарсился
        """
        page = self._get_tournament_page(tournament_id)

        # Если page пустая, значит была ошибка 404 и турнир удалили
        if page == '':
            return {}, False

        tournament_obj = TournamentParser.parse_data(page)
        if tournament_obj is None:
            raise RuntimeError('Parsing is failed')

        # Обновляем поле players в таблице tournaments
        all_players = [player.id for player in tournament_obj.registered_players]
        all_players += [player.id for player in tournament_obj.refused_players]
        all_players = list(set(all_players))
        sorted(all_players)

        with open_session() as session:
            tournament = (
                session.query(DBTournament)
                .filter_by(id=tournament_id)
                .first()
            )
            if tournament is None:
                raise RuntimeError(f"tournament_id {tournament_id} должен быть в таблице tournaments")
            tournament.set_players(all_players)
            session.commit()

        players_dict: dict[int, PlayerTournamentInfo] = {}

        # TODO: формирование этих объектов должно быть внутри парсинга
        # Объединяем парсинг таблиц записавшихся, отказавшихся и сыгравших
        # в один объект
        for player in tournament_obj.registered_players:
            if player.id not in players:
                continue
            players_dict[player.id] = PlayerTournamentInfo(
                player_id=player.id,
                player_name=player.name,
                tournament_id=tournament_id,
                tournament_name=tournament_obj.name,
                status='registered',
            )
        for player in tournament_obj.refused_players:
            if player.id not in players:
                continue
            players_dict[player.id] = PlayerTournamentInfo(
                player_id=player.id,
                player_name=player.name,
                tournament_id=tournament_id,
                tournament_name=tournament_obj.name,
                status='refused',
            )
        for result in tournament_obj.player_results:
            if result.player_id not in players:
                continue
            players_dict[result.player_id] = PlayerTournamentInfo(
                player_id=result.player_id,
                player_name=result.name,
                tournament_id=tournament_id,
                tournament_name=tournament_obj.name,
                status='completed',
                rating_before=result.rating_before,
                rating_delta=result.rating_delta,
                rating_after=result.rating_after,
                games_won=result.games_won,
                games_lost=result.games_lost,
            )

        # Смотрим на то, что лежит в базе
        # Если появилось новое или обновилось старое - посылаем нотификацию
        updated = {}
        with open_session() as session:
            for player_id, info in players_dict.items():
                existing = (
                    session.query(DBPlayerTournament)
                    .filter_by(tournament_id=tournament_id, player_id=player_id)
                    .first()
                )
                serialized = info.serialize()
                if existing is None:
                    new_record = DBPlayerTournament(
                        player_id=player_id,
                        tournament_id=tournament_id,
                        info_json=serialized,
                    )
                    session.add(new_record)
                    updated[player_id] = info
                elif existing.info_json != serialized:
                    existing.info_json = serialized
                    updated[player_id] = info
            session.commit()

        return updated, True

    def process_batch_and_notify(
        self, batch_size: int, now: Optional[datetime.datetime] = None
    ):
        all_updates = []
        if now is None:
            now = datetime.datetime.now()
        with open_session() as session:
            expired_tournaments: list[DBTournament] = (
                session.query(DBTournament)
                .filter(DBTournament.next_update_dtm < now.timestamp())
                .limit(batch_size)
                .all()
            )
            if not expired_tournaments:
                return all_updates

            subscriptions = self._get_subscriptions_dict()
            unique_players = set(subscriptions.keys())

            for tournament in expired_tournaments:
                updates, is_ok = self._update_player_tournaments(
                    unique_players, tournament.id
                )

                # Если турнир пропал с сайта перестаем его обовлять
                if not is_ok:
                    tournament.next_update_dtm = None
                    session.commit()
                    continue

                # Главное - не поломаться в этот момент
                # Если update отработает, а нотификации не отправятся, то мы их потеряем
                # Можно сделать надежнее, но пока так
                for player_id, info in updates.items():
                    if player_id in subscriptions:
                        for user_id in subscriptions[player_id]:
                            self._send_player_update(user_id, info)

                # Установка времени следующего апдейта турнира
                if tournament.tournament_date < (
                    now.date() - datetime.timedelta(days=3)
                ):
                    tournament.next_update_dtm = None
                else:
                    tournament.next_update_dtm = now.timestamp() + 3600 * 2
                # Если батч упадет посередине, то отработавшая часть не перезапустится
                session.commit()
                all_updates.extend(updates)
        return all_updates
