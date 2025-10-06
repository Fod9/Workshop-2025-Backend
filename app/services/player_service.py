from __future__ import annotations

from typing import List, Optional

from sqlmodel import select

from app.services.db_service import DBService
from models import Player


class PlayerService:
    def __init__(self, db_service: Optional[DBService] = None) -> None:
        self.db_service = db_service or DBService()

    def create_player(self, username: str) -> Player:
        with self.db_service.session() as session:
            player = Player(username=username)
            session.add(player)
            session.commit()
            session.refresh(player)
            return player

    def get_player_by_username(self, username: str) -> Optional[Player]:
        with self.db_service.session() as session:
            statement = select(Player).where(Player.username == username)
            return session.exec(statement).first()

    def list_players(self) -> List[Player]:
        with self.db_service.session() as session:
            return session.exec(select(Player)).all()

    def list_tables(self) -> list[str]:
        statement = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
        rows = self.db_service.execute(statement)
        return [row[0] for row in rows]

    def raw_query(self, query: str, params: Optional[dict] = None):
        return self.db_service.execute(query, params)
