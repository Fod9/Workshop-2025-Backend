from __future__ import annotations

import asyncio
import json
import random
import secrets
import string
from collections.abc import Sequence
from typing import TYPE_CHECKING, Dict, List, Optional

if TYPE_CHECKING:
    from app.services.websocket_manager import ConnectionManager

from sqlmodel import select
from app.services.db_service import DBService
from sqlalchemy.exc import IntegrityError
from models import Game, Player, PlayerRead

_GAME_LOCKS: Dict[int, asyncio.Lock] = {}
_LOCKS_GUARD: asyncio.Lock | None = None


class GameService:
    CONTINENTS = ["Europe", "Asie", "Afrique", "Amerique"]

    def __init__(self, db_service: Optional[DBService] = None) -> None:
        self.db_service = db_service or DBService()

    async def _get_game_lock(self, game_id: int) -> asyncio.Lock:
        global _LOCKS_GUARD
        if _LOCKS_GUARD is None:
            _LOCKS_GUARD = asyncio.Lock()

        async with _LOCKS_GUARD:
            lock = _GAME_LOCKS.get(game_id)
            if lock is None:
                lock = asyncio.Lock()
                _GAME_LOCKS[game_id] = lock
            return lock

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

    async def join_game_by_code(self, join_code: str, player_name: str, manager: "ConnectionManager") -> Game:
        join_code = join_code.strip().upper()
        with self.db_service.session() as session:
            game = session.exec(
                select(Game).where(Game.join_code == join_code)
            ).first()
            if game is None:
                raise ValueError("Invalid join code")
            game_id = game.id

        lock = await self._get_game_lock(game_id)
        json_content: str | None = None
        joined_game: Game | None = None
        async with lock:
            with self.db_service.session() as session:
                game = session.exec(select(Game).where(Game.id == game_id)).first()
                if game is None:
                    raise ValueError("Invalid join code")

                existing_name = session.exec(
                    select(Player)
                    .where(Player.game_id == game_id)
                    .where(Player.name == player_name)
                ).first()
                if existing_name:
                    raise ValueError("Name already taken in this game")

                attempts_remaining = len(self.CONTINENTS)
                while attempts_remaining:
                    continent = self._assign_continent(session, game_id)
                    player = Player(
                        game_id=game_id,
                        name=player_name,
                        is_host=False,
                        continent=continent,
                        )
                    session.add(player)
                    try:
                        session.commit()
                    except IntegrityError:
                        session.rollback()
                        attempts_remaining -= 1
                        continue

                    session.refresh(game)
                    session.refresh(game, attribute_names=["players"])
                    player_payload = PlayerRead.model_validate(player).model_dump()
                    json_content = json.dumps(
                        {
                            "type": "player_joined",
                            "data": player_payload,
                        }
                    )
                    joined_game = game
                    session.expunge(game)
                    break

                else:
                    raise ValueError("No continents available for this game")

        if json_content is None:
            raise ValueError("No continents available for this game")

        await manager.broadcast(json_content, game_id)
        if joined_game is None:
            raise ValueError("No continents available for this game")

        return joined_game

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

    async def continue_game(self, game_id: int, manager: "ConnectionManager") -> Game:
        with self.db_service.session() as session:
            game = session.exec(
                select(Game).where(Game.id == game_id)
            ).first()
            if game is None:
                raise ValueError("Invalid game ID")

            game.stage += 1
            session.add(game)
            session.commit()
            session.refresh(game)
            session.refresh(game, attribute_names=["players"])
            players = self.list_players(game_id)
            player_payloads = [PlayerRead.model_validate(p).model_dump() for p in players]
            json_content = json.dumps(
                {
                    "type": "game_continued",
                    "data": {
                        "stage": game.stage,
                        "players": player_payloads,
                    },
                }
            )

        await manager.broadcast(json_content, game_id)

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
        taken: set[str] = set()
        for row in session.exec(
            select(Player.continent)
            .where(Player.game_id == game_id)
            .where(Player.continent.is_not(None))
        ):
            if isinstance(row, str):
                value = row
            elif isinstance(row, Sequence) and row:
                value = row[0]
            else:
                value = getattr(row, "continent", None)

            if value:
                taken.add(value)
        available = [continent for continent in self.CONTINENTS if continent not in taken]
        if not available:
            raise ValueError("No continents available for this game")
        return random.choice(available)
