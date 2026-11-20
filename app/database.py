from collections.abc import Generator

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


class Base(DeclarativeBase):
    pass


class Database:
    """Own the engine and session factory for one application instance."""

    def __init__(self, url: str) -> None:
        connect_args = {"check_same_thread": False, "timeout": 30} if url.startswith("sqlite") else {}
        self.engine: Engine = create_engine(url, connect_args=connect_args)
        self.session_factory = sessionmaker(
            bind=self.engine,
            autoflush=False,
            expire_on_commit=False,
        )

        if url.startswith("sqlite"):
            event.listen(self.engine, "connect", self._configure_sqlite)

    @staticmethod
    def _configure_sqlite(dbapi_connection: object, _: object) -> None:
        cursor = dbapi_connection.cursor()  # type: ignore[attr-defined]
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA busy_timeout=30000")
        cursor.close()

    def create_tables(self) -> None:
        Base.metadata.create_all(self.engine)

    def session(self) -> Generator[Session, None, None]:
        db = self.session_factory()
        try:
            yield db
        finally:
            db.close()

    def dispose(self) -> None:
        self.engine.dispose()
