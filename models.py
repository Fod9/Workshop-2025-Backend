from typing import List, Optional

from sqlalchemy import Column, String
from sqlmodel import Field, Relationship, SQLModel

from app.services.db_service import DBService

class Game(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(sa_column=Column("name", String, unique=True, index=True))
    stage: int = Field(default=1)
    join_code: str = Field(sa_column=Column("join_code", String, unique=True, index=True))
    host_name: str = Field(sa_column=Column("host_name", String, index=True))
    participants: List["Participant"] = Relationship(back_populates="game", sa_relationship_kwargs={"cascade": "all, delete-orphan"})

    def __repr__(self) -> str:
        return f"<Game(name={self.name}, stage={self.stage}, join_code={self.join_code})>"


class Participant(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    game_id: int = Field(foreign_key="game.id")
    name: str = Field(sa_column=Column("name", String, index=True))
    is_host: bool = Field(default=False)

    game: Optional[Game] = Relationship(back_populates="participants")

    def __repr__(self) -> str:
        return f"<Participant(name={self.name}, game_id={self.game_id}, is_host={self.is_host})>"


def init_db():
    db_service = DBService()
    db_service.create_database()
