from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlmodel import Session, create_engine


class DBService:
    def __init__(self, database_url: str | None = None) -> None:
        self._db_path = Path(__file__).resolve().parents[2] / "app.db"
        self._database_url = database_url or f"sqlite:///{self._db_path}"
        self._engine = create_engine(
            self._database_url,
            connect_args={"check_same_thread": False},
            pool_pre_ping=True,
        )

    @property
    def engine(self) -> Engine:
        return self._engine

    @property
    def database_url(self) -> str:
        return self._database_url

    @property
    def db_path(self) -> str:
        return str(self._db_path)

    @contextmanager
    def session(self) -> Iterator[Session]:
        with Session(self._engine) as session:
            yield session

    def create_database(self) -> None:
        from sqlmodel import SQLModel

        SQLModel.metadata.create_all(self._engine)

    def execute(self, statement: str, params: dict[str, Any] | None = None):
        with self.engine.begin() as connection:
            result = connection.execute(text(statement), params or {})
            return result.all()

    def query(self, query: str, params: dict[str, Any] | None = None):
        return self.execute(query, params)
