from typing import Optional, List

from sqlalchemy import Column, Integer, String
from sqlmodel import Field, SQLModel

from app.services.db_service import DBService


class Player(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(sa_column=Column("username", String, unique=True, index=True))

    def __repr__(self) -> str:
        return f"<Player(username={self.username})>"


class Game(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    room_master_id: Optional[int] = Field(default=None, foreign_key="player.id")
    name: str = Field(sa_column=Column("name", String, unique=True, index=True))
    stage: int = Field(default=1)

    def __repr__(self) -> str:
        return f"<Game(name={self.name}, stage={self.stage})>"

class Invitattion(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    from_player_id: Optional[int] = Field(default=None, foreign_key="player.id")
    to_player_id: Optional[int] = Field(default=None, foreign_key="player.id")
    game_id: Optional[int] = Field(default=None, foreign_key="game.id")
    status: str = Field(default="pending")  # pending, accepted, rejected

    def __repr__(self) -> str:
        return f"<Invitation(from_player_id={self.from_player_id}, to_player_id={self.to_player_id}, game_id={self.game_id})>"

class GamePlayerLink(SQLModel, table=True):
    game_id: Optional[int] = Field(default=None, foreign_key="game.id", primary_key=True)
    player_id: Optional[int] = Field(default=None, foreign_key="player.id", primary_key=True)

    def __repr__(self) -> str:
        return f"<GamePlayerLink(game_id={self.game_id}, player_id={self.player_id})>"


def init_db():
    db_service = DBService()
    db_service.create_database()
