from sqlmodel import Column, Integer, String, SQLModel, Field

from app.services.db_service import DBService


class Player(SQLModel, table=True):
    id: int = Column(Integer, primary_key=True)
    username: str = Column(String, unique=True, index=True)

    def __repr__(self):
        return f"<Player(name={self.name}, age={self.age}, team={self.team})>"

class Game(SQLModel, table=True):
    id: int = Column(Integer, primary_key=True)
    name: str = Column(String, unique=True, index=True)
    stage: str = Column(Integer, default=1)
    players: list[Player] = Field(default_factory=list, foreign_key="player.id")
    
    def __repr__(self):
        return f"<Game(name={self.name})>"


def init_db():
    db_service = DBService()
    db_service.create_database()
