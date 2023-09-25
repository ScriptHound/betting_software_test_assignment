import os
import asyncio
from typing import Optional
from unittest.mock import patch

import pytest
import httpx
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from testcontainers.postgres import PostgresContainer

from src.database.settings import Base
from main import app
from src.views.bets.schemas import EventState
from tests.fixtures import *  # noqa
import src.database.settings as database_session_mock_target
import src.views.bets.logic as line_provider_mock_target


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
        self.test_engine = create_async_engine(self.connection_url)
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


@pytest.fixture(scope="session")
async def get_testing_session_manager_class(async_DAL_fixture):
    class SessionManagerTest:
        def __init__(self, session: Optional[AsyncSession] = None):
            self.session = session or async_DAL_fixture.TestSession()  # type: ignore
            self.autoclose = session is None

        async def __aenter__(self) -> AsyncSession:
            self.session = async_DAL_fixture.TestSession()
            return self.session

        async def __aexit__(self, exc_type, exc, tb):
            if exc_type is not None:
                await self.session.rollback()
            else:
                await self.session.commit()

            if self.autoclose:
                await self.session.close()

    return SessionManagerTest


@pytest.fixture(scope="session")
async def mock_database_session(get_testing_session_manager_class):
    with patch.object(
        database_session_mock_target,
        "SessionManager",
        get_testing_session_manager_class,
    ):
        yield


@pytest.fixture(scope="session")
async def mock_line_provider():
    class MockLineProviderClient:
        @staticmethod
        async def get_all_events_data_from_line_provider(http_client):
            events = [
                {
                    "event_id": "1",
                    "coefficient": 1.2,
                    "deadline": 1600,
                    "state": EventState.NEW.value,
                },
                {
                    "event_id": "2",
                    "coefficient": 1.15,
                    "deadline": 1060,
                    "state": EventState.NEW.value,
                },
                {
                    "event_id": "3",
                    "coefficient": 1.67,
                    "deadline": 1090,
                    "state": EventState.NEW.value,
                },
            ]
            return events

    with patch.object(
        line_provider_mock_target, "LineProviderClient", MockLineProviderClient
    ):
        yield
