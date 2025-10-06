from __future__ import annotations

import secrets
import string
from typing import List, Optional

from sqlmodel import select

from app.services.db_service import DBService
from models import Game, Participant


class GameService:
    def __init__(self, db_service: Optional[DBService] = None) -> None:
        self.db_service = db_service or DBService()

    def create_game(self, name: str, host_name: str) -> Game:
        with self.db_service.session() as session:
            join_code = self._generate_unique_code(session)
            game = Game(name=name, host_name=host_name, join_code=join_code)
            session.add(game)
            session.flush()

            session.add(Participant(game_id=game.id, name=host_name, is_host=True))
            session.commit()
            session.refresh(game)
            return game

    def join_game_by_code(self, join_code: str, participant_name: str) -> Game:
        join_code = join_code.strip().upper()
        with self.db_service.session() as session:
            game = session.exec(
                select(Game).where(Game.join_code == join_code)
            ).first()
            if game is None:
                raise ValueError("Invalid join code")

            existing_name = session.exec(
                select(Participant)
                .where(Participant.game_id == game.id)
                .where(Participant.name == participant_name)
            ).first()
            if existing_name:
                raise ValueError("Name already taken in this game")

            participant = Participant(game_id=game.id, name=participant_name, is_host=False)
            session.add(participant)
            session.commit()
            session.refresh(game)
            return game

    def list_participants(self, game_id: int) -> List[Participant]:
        with self.db_service.session() as session:
            return session.exec(
                select(Participant).where(Participant.game_id == game_id)
            ).all()

    def _generate_unique_code(self, session, length: int = 6) -> str:
        alphabet = string.ascii_uppercase + string.digits
        while True:
            code = "".join(secrets.choice(alphabet) for _ in range(length))
            existing = session.exec(select(Game).where(Game.join_code == code)).first()
            if existing is None:
                return code
