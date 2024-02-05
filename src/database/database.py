from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncEngine,
    AsyncSession,
)
from sqlalchemy_utils.functions import create_database, database_exists

from src.config import config
from . import models


class Database:
    engine: AsyncEngine
    session_maker: async_sessionmaker

    def __init__(self) -> None:
        self.engine = create_async_engine(config.database.url)
        self.session_maker = async_sessionmaker(
            self.engine, expire_on_commit=False
        )

    async def init_database(self) -> None:
        url = config.database.url_sync

        if database_exists(url):
            return

        create_database(url)
        async with self.engine.begin() as connection:
            await connection.run_sync(models.Base.metadata.create_all)

    def create_session(self) -> AsyncSession:
        return self.session_maker()


database = Database()
