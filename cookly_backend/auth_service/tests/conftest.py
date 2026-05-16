import os
from collections.abc import AsyncGenerator
from pathlib import Path
from typing import Any, TypedDict
from unittest.mock import MagicMock
from uuid import UUID

os.environ["PRIVATE_KEY_PATH"] = str(
    Path(__file__).resolve().parent.parent.parent / "certs" / "jwt-private.pem"
)
os.environ["PUBLIC_KEY_PATH"] = str(
    Path(__file__).resolve().parent.parent.parent / "certs" / "jwt-public.pem"
)
os.environ["REDIS_HOST"] = "localhost"

import docker
import pytest
from alembic import command
from alembic.config import Config
from dishka import (
    AsyncContainer,
    Provider,
    Scope,
    make_async_container,
    provide,
)
from dishka.integrations.fastapi import setup_dishka
from httpx import AsyncClient
from sqlalchemy import NullPool, text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from starlette.requests import Request

from application.common.auth_server_token_types import Fingerprint
from application.common.interfaces.http_auth import HttpAuthServerService
from application.common.interfaces.user_repo import UserRepository
from auth_service.tests.config import TEST_DATABASE_URI
from core.di.container import prod_provders
from domain.common.services.pwd_service import PasswordHasher
from domain.entities.client.model import Client
from domain.entities.client.value_objects import ClientTypeEnum
from domain.entities.resource_server.model import ResourceServer
from domain.entities.resource_server.value_objects import ResourceServerType
from domain.entities.role.model import Role
from domain.entities.user.model import User
from domain.entities.user.value_objects import UserID
from infrastructure.db.repositories.user_repo_impl import UserRepositoryImpl
from presentation.web_api.main import create_app


os.environ["USE_NULLPOOL"] = "true"


class MockRequestProvider(Provider):
    @provide(provides=Request, scope=Scope.REQUEST)
    async def provide_request(self) -> Request:
        mock = MagicMock(spec=Request)
        mock.headers = {
            "X-Device-Fingerprint": "5efe7689dab485b716bc0f9161e4479f046c076e317867adb562a510b7f1c52b",
            "authorization": "Bearer ",
        }
        mock.cookies = {}
        return mock


@pytest.fixture(scope="session")
async def container(redis_container, nats_container) -> AsyncContainer:
    container = make_async_container(*prod_provders, MockRequestProvider())
    yield container
    await container.close()


@pytest.fixture()
async def rq_container(container: AsyncContainer):
    async with container(scope=Scope.REQUEST) as request_container:
        yield request_container


@pytest.fixture(scope="session", autouse=True)
def apply_migrations():
    current_working_directory = os.getcwd()

    project_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../")
    )
    os.chdir(project_root)

    try:
        alembic_cfg = Config(
            os.path.join(os.path.dirname(__file__), "../alembic.ini")
        )
        alembic_cfg.set_main_option("sqlalchemy.url", TEST_DATABASE_URI)
        command.upgrade(alembic_cfg, "head")
    finally:
        os.chdir(current_working_directory)


@pytest.fixture(scope="session")
async def async_engine(container: AsyncContainer) -> AsyncEngine:
    os.environ["DATABASE_URI"] = TEST_DATABASE_URI
    return create_async_engine(
        url=TEST_DATABASE_URI, echo=True, poolclass=NullPool
    )


@pytest.fixture(scope="session")
async def session_maker(
    async_engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(bind=async_engine, expire_on_commit=False)


@pytest.fixture(scope="function")
async def async_session(
    session_maker: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[Any, Any]:
    async with session_maker() as session:
        yield session


@pytest.fixture(scope="function")
async def real_user_repo(async_session: AsyncSession) -> UserRepository:
    return UserRepositoryImpl(session=async_session)


@pytest.fixture(scope="session")
async def ac(container) -> AsyncGenerator[AsyncClient, None]:
    app = create_app()
    setup_dishka(container, app)
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="session")
async def ph(container: AsyncContainer) -> PasswordHasher:
    return await container.get(PasswordHasher)


@pytest.fixture(scope="session", autouse=True)
async def teardown_database(async_engine: AsyncEngine):
    """Удаление тестовой базы данных после завершения всех тестов."""
    yield
    async with async_engine.begin() as conn:
        await conn.execute(text("DROP SCHEMA public CASCADE;"))
        await conn.execute(text("CREATE SCHEMA public;"))


class StaticEntities(TypedDict):
    roles: list[Role]
    client: Client
    user: User


@pytest.fixture(scope="session")
def static_entities() -> dict:
    """Возвращает данные для создания сущностей."""
    return {
        "client": {
            "name": "Test Client",
            "base_url": "http://test",
            "allowed_redirect_urls": ["http://test"],
            "type": ClientTypeEnum.PUBLIC,
        },
        "roles": [
            {
                "name": "Admin",
                "base_scopes": {"scope1": "1011", "scope2": "1011"},
            },
            {
                "name": "User",
                "base_scopes": {"scope1": "0011", "scope2": "0111"},
            },
        ],
        "user": {
            "user_id": UUID("e768a26d-8984-4b65-8d3c-f9122cc6245e"),
            "email": "admin@test.com",
            "raw_password": "string",
        },
    }


@pytest.fixture(scope="session", autouse=True)
async def populate_database(
    static_entities, session_maker, ph: PasswordHasher
):
    """Наполняет базу данных статическими сущностями перед тестами."""
    async with session_maker() as async_session:
        client = Client.create(**static_entities["client"])
        async_session.add(client)
        rs = ResourceServer.create(
            name="test_server", type=ResourceServerType.RBAC_BY_AS
        )
        async_session.add(rs)
        await async_session.flush()
        await async_session.refresh(client)
        await async_session.refresh(rs)

        roles = [
            Role.create(rs_id=rs.id, **role_data)
            for role_data in static_entities["roles"]
        ]
        async_session.add_all(roles)
        await async_session.flush(roles)
        await async_session.refresh(roles[0])
        await async_session.refresh(roles[1])

        user = User.create(**static_entities["user"], password_hasher=ph)
        async_session.add(user)
        await async_session.commit()


@pytest.fixture
async def admin_role(async_session):
    """Фикстура для получения роли Admin."""
    return await async_session.scalar(
        text("SELECT * FROM roles WHERE name = 'Admin' LIMIT 1")
    )


@pytest.fixture
async def user_role_in_db(async_session):
    """Фикстура для получения роли User."""
    return await async_session.scalar(
        text("SELECT * FROM roles WHERE name = 'User' LIMIT 1")
    )


@pytest.fixture
async def client_in_db(async_session):
    """Фикстура для получения клиента."""
    return await async_session.scalar(
        text("SELECT * FROM clients WHERE name = 'Test Client' LIMIT 1")
    )


@pytest.fixture
async def user_in_db(async_session):
    """Фикстура для получения пользователя."""
    return await async_session.get(
        User, UserID(UUID("e768a26d-8984-4b65-8d3c-f9122cc6245e"))
    )


@pytest.fixture(autouse=True)
async def rollback_on_db_mutation(request, async_session):
    """Откатывает изменения базы данных после тестов с меткой `db_mutation`."""
    if "db_mutation" in request.keywords:
        async with async_session.begin_nested():
            yield
            await async_session.rollback()
    else:
        yield


@pytest.fixture
async def auth_headers(mock_user: User, container) -> dict:
    """
    Фикстура для получения заголовков с авторизацией.
    """
    headers = {"Fingerprint": "3ccc784000c0c0c11cab8508dffaa578"}
    http_auth_service = await container.get(HttpAuthServerService)
    access_token, refresh_token = http_auth_service.create_and_save_tokens(
        mock_user, Fingerprint("3ccc784000c0c0c11cab8508dffaa578")
    )

    headers["Authorization"] = f"Bearer {access_token}"
    return headers


@pytest.fixture(scope="session")
def redis_container():
    """Запускает Redis в Docker на порту 6379."""
    client = docker.from_env()
    container = client.containers.run(
        "redis:latest",
        ports={"6378/tcp": 6378},
        detach=True,
    )
    yield container
    container.stop()
    container.remove()


@pytest.fixture(scope="session")
def nats_container():
    """Запускает NATS в Docker на порту 4222."""
    client = docker.from_env()
    container = client.containers.run(
        "nats:latest",
        ports={"4223/tcp": 4223},
        detach=True,
    )
    yield container
    container.stop()
    container.remove()


@pytest.fixture
async def nats_client(container: AsyncContainer):
    nats_client = await container.get(Client)
    return nats_client


@pytest.fixture
async def redis_client(container):
    import redis.asyncio as aioredis

    client = await container.get(aioredis.Redis)
    yield client
    await client.flushall()
