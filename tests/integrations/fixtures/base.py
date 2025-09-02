import pytest_asyncio
from httpx import AsyncClient

from application.main import app


@pytest_asyncio.fixture(scope="function")
async def ac():
    """Асинхронный HTTP-клиент для тестов"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
