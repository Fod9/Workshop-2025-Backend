from __future__ import annotations

import random
import secrets
import string
from typing import List, Optional

from sqlmodel import select
from app.services.db_service import DBService
from models import Game, Player


class GameService:
    def __init__(self, db_service: Optional[DBService] = None) -> None:
        self.db_service = db_service or DBService()

    def create_game(self, name: str, host_name: str) -> Game:
        with self.db_service.session() as session:
            join_code = self._generate_unique_code(session)
            game = Game(name=name, host_name=host_name, join_code=join_code)
            session.add(game)
            session.flush()

            continent = self._assign_continent(session, game.id)
            session.add(
                Player(
                    game_id=game.id,
                    name=host_name,
                    is_host=True,
                    continent=continent,
                )
            )
            session.commit()
            session.refresh(game)
            session.refresh(game, attribute_names=["players"])
            return game

    def join_game_by_code(self, join_code: str, player_name: str) -> Game:
        join_code = join_code.strip().upper()
        with self.db_service.session() as session:
            game = session.exec(
                select(Game).where(Game.join_code == join_code)
            ).first()
            if game is None:
                raise ValueError("Invalid join code")

            existing_name = session.exec(
                select(Player)
                .where(Player.game_id == game.id)
                .where(Player.name == player_name)
            ).first()
            if existing_name:
                raise ValueError("Name already taken in this game")

            continent = self._assign_continent(session, game.id)
            player = Player(
                game_id=game.id,
                name=player_name,
                is_host=False,
                continent=continent,
            )
            session.add(player)
            session.commit()
            session.refresh(game)
            session.refresh(game, attribute_names=["players"])
            return game

    def delete_game(self, join_code: str, host_name: str) -> Game:
        join_code = join_code.strip().upper()
        with self.db_service.session() as session:
            game = session.exec(
                select(Game).where(Game.join_code == join_code)
            ).first()
            if game is None:
                raise ValueError("Invalid join code")
            if game.host_name != host_name:
                raise ValueError("Only the host can delete the game")

            session.delete(game)
            session.commit()
            return game

    def list_players(self, game_id: int) -> List[Player]:
        with self.db_service.session() as session:
            return session.exec(
                select(Player).where(Player.game_id == game_id)
            ).all()

    def _generate_unique_code(self, session, length: int = 6) -> str:
        alphabet = string.ascii_uppercase + string.digits
        while True:
            code = "".join(secrets.choice(alphabet) for _ in range(length))
            existing = session.exec(select(Game).where(Game.join_code == code)).first()
            if existing is None:
                return code

    def _assign_continent(self, session, game_id: int) -> str:
        continents = ["Europe", "Asie", "Afrique", "Amerique"]
        taken = {
            row[0]
            for row in session.exec(
                select(Player.continent)
                .where(Player.game_id == game_id)
                .where(Player.continent.is_not(None))
            )
            if row[0]
        }
        available = [continent for continent in continents if continent not in taken]
        if not available:
            raise ValueError("No continents available for this game")
        return random.choice(available)
