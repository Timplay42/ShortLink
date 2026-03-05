import sqlalchemy.engine.url as SQURL

from sqlalchemy import exc, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from Shared.Config import Settings

settings = Settings()

class AsyncDatabaseSessions:

    def __init__(self):
        self.URL = SQURL.URL.create(
            drivername=settings.db.drivername,
            username=settings.db.username,
            password=settings.db.password,
            host=settings.db.host,
            port=settings.db.port,
            database=settings.db.database,
        )
        self.engine = create_async_engine(
            self.URL, pool_size=200, max_overflow=-1, pool_pre_ping=True
        )
        self.factory = async_sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    def get_url(self):
        return str(self.URL)

    def get_session_maker(self) -> async_sessionmaker:
        return self.factory

    async def get_session(self) -> AsyncSession:
        async with self.factory() as session:
            try:
                yield session
            except exc.SQLAlchemyError as error:
                await session.rollback()
                raise

    async def return_session(self):
        return self.factory()


AsyncDatabase = AsyncDatabaseSessions()
