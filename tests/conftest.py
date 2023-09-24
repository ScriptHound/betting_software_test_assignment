import os
import asyncio

import pytest
import httpx
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from testcontainers.postgres import PostgresContainer

from src.database.settings import Base
from main import app


@pytest.fixture
async def async_http_client():
    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture(scope="session", autouse=True)
def event_loop():
    loop = asyncio.new_event_loop()
    try:
        yield loop
    finally:
        loop.close()


class PatchedPostgresContainer(PostgresContainer):
    # https://github.com/testcontainers/testcontainers-python/issues/108
    # Fix bug with name resolution on Windows hosts
    _container = None

    def get_container_host_ip(self) -> str:
        return "localhost" if os.name == "nt" else super().get_container_host_ip()



class AsyncTestDataAccessLayer:
    def __init__(self, container: "PatchedPostgresContainer"):
        self.connection_url = container.get_connection_url()
        self.test_engine = create_async_engine(
            self.connection_url, execution_options={"isolation_level": "REPEATABLE READ"}
        )
        self.TestSession = sessionmaker(
            self.test_engine,
            class_=AsyncSession,  # type: ignore
            autoflush=True,
            autocommit=False,
            expire_on_commit=False,
        )

    async def setup_database(self):
        async with self.test_engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)  # type: ignore
        await self.test_engine.dispose()


@pytest.fixture(scope="session")
async def postgresql_container():
    with PatchedPostgresContainer("postgres:14") as postgres_container:
        postgres_container.driver = "asyncpg"
        yield postgres_container


@pytest.fixture(scope="session")
async def async_DAL_fixture(postgresql_container):
    test_dal = AsyncTestDataAccessLayer(postgresql_container)
    await test_dal.setup_database()
    return test_dal


@pytest.fixture
async def async_testing_session(async_DAL_fixture: AsyncTestDataAccessLayer):
    session = async_DAL_fixture.TestSession
    async with session() as transaction:  # type: ignore
        try:
            yield transaction
            await transaction.commit()
        finally:
            await transaction.rollback()
