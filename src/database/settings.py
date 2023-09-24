from collections.abc import AsyncGenerator
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from src.settings.env_settings import Settings


async_engine = create_async_engine(
    Settings.POSTGRESQL_URI,
    pool_size=50,
    pool_pre_ping=True,
    pool_recycle=300,
    # echo=True,
)

AsyncSessionMaker: AsyncSession = sessionmaker(
    async_engine,
    class_=AsyncSession,  # type: ignore
    autoflush=True,
    autocommit=False,
    expire_on_commit=False,
)


class SessionManager:
    def __init__(self, session: Optional[AsyncSession] = None):
        self.session = session or AsyncSessionMaker()  # type: ignore
        self.autoclose = session is None

    async def __aenter__(self) -> AsyncSession:
        return self.session

    async def __aexit__(self, exc_type, exc, tb):
        if exc_type is not None:
            await self.session.rollback()
        else:
            await self.session.commit()

        if self.autoclose:
            await self.session.close()


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionManager() as session:
        yield session


Base = declarative_base()
