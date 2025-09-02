import pytest
import pytest_asyncio

from application.database import async_session, async_engine
from application.auth.models import User
from application.utils.tokens import JWTTokenService


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_db():
    """
    Фикстура для создания таблицы User перед тестами
    и удаления после тестов.
    """
    async with async_engine.begin() as conn:
        await conn.run_sync(
            lambda sync_conn: User.metadata.create_all(bind=sync_conn)
        )

    yield

    async with async_engine.begin() as conn:
        await conn.run_sync(User.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def test_user():
    async with async_session() as session:
        user = User(
            email="testuser@test.com",
            hash_password="$2b$12$jY7D8CoOfJSRrrLDx8kXbuyPXvP02g.7SlcNLsST13S238ji.a.gy",
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        yield user
    async with async_session() as session2:
        await session2.delete(user)
        await session2.commit()


@pytest_asyncio.fixture()
async def access_and_refresh_tokens_test_user(test_user: User):
    return JWTTokenService.create_access_and_refresh_tokens(
        {"id": test_user.id}
    )


@pytest_asyncio.fixture()
async def access_and_refresh_tokens_invalid_user():
    return JWTTokenService.create_access_and_refresh_tokens({"id": 1000})


@pytest.fixture()
def login_invalid_data():
    """Фикстура для получения данных не зарегестрированного пользователя
    Returns:
        dict[str]: Данные не зарегестрированного пользователя
    """
    return {"email": "notexistuser@test.com", "password": "12345678"}


@pytest.fixture()
def user_registration_data():
    """Фикстура для получения данных пользователя для регистрации
    Returns:
        dict[str]: Данные пользователя для регистрации
    """
    return {"email": "testuser2@test.com", "password": "lnflsnsdjl"}
