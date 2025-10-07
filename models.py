from typing import List, Optional

from sqlalchemy import Column, String, UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel
from pydantic import ConfigDict

from app.services.db_service import DBService

class Game(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(sa_column=Column("name", String, unique=True, index=True))
    stage: int = Field(default=0)
    join_code: str = Field(sa_column=Column("join_code", String, unique=True, index=True))
    host_name: str = Field(sa_column=Column("host_name", String, index=True))
    players: List["Player"] = Relationship(
        back_populates="game",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "lazy": "selectin",
        },
    )

    def __repr__(self) -> str:
        return f"<Game(name={self.name}, stage={self.stage}, join_code={self.join_code})>"


class Player(SQLModel, table=True):
    __tablename__ = "participant"
    __table_args__ = (
        UniqueConstraint("game_id", "continent", name="uq_player_game_continent"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    game_id: int = Field(foreign_key="game.id")
    name: str = Field(sa_column=Column("name", String, index=True))
    is_host: bool = Field(default=False)
    continent: str = Field(sa_column=Column("continent", String, index=True))

    game: Optional[Game] = Relationship(back_populates="players")

    def __repr__(self) -> str:
        return f"<Player(name={self.name}, game_id={self.game_id}, is_host={self.is_host})>"


class PlayerRead(SQLModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    game_id: int
    name: str
    is_host: bool
    continent: str


class GameRead(SQLModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    stage: int
    join_code: str
    host_name: str
    players: List[PlayerRead] = Field(default_factory=list)


def init_db():
    db_service = DBService()
    db_service.create_database()
