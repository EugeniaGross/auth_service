import pytest
from httpx import AsyncClient

from .fixtures.auth import (
    setup_test_db,
    login_invalid_data,
    test_user,
    user_registration_data,
    access_and_refresh_tokens_test_user,
    access_and_refresh_tokens_invalid_user,
)
from .fixtures.base import ac
from application.auth.models import User


@pytest.mark.asyncio
async def test_registration_with_valid_data(
    ac: AsyncClient, user_registration_data: dict
):
    response = await ac.post(
        "/api/v1/registration/", json=user_registration_data
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["email"] == user_registration_data["email"]


@pytest.mark.asyncio
async def test_registration_with_existing_user(
    ac: AsyncClient, test_user: User
):
    response = await ac.post(
        "/api/v1/registration/",
        json={"email": test_user.email, "password": "password"},
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_login_with_valid_data(ac: AsyncClient, test_user: User):
    response = await ac.post(
        "/api/v1/login/",
        json={"email": test_user.email, "password": "12345678"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "access_token_expire" in data
    assert data["token_type"] == "bearer"
    cookie_header = response.headers.get("set-cookie")
    assert "resumes_token" in cookie_header


@pytest.mark.asyncio
async def test_login_with_invalid_data(
    ac: AsyncClient, login_invalid_data: dict
):
    response = await ac.post("/api/v1/login/", json=login_invalid_data)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_get_jwt_public_key(ac: AsyncClient):
    response = await ac.get("/api/v1/jwt.key")
    assert response.status_code == 200
    data = response.json()
    assert "public_key" in data


@pytest.mark.asyncio
async def test_logout(ac: AsyncClient):
    response = await ac.post("/api/v1/logout/")
    assert response.status_code == 200
    set_cookie = response.headers.get("set-cookie", "")
    assert set_cookie.startswith("resumes_token=")
    assert "Max-Age=0" in set_cookie


@pytest.mark.asyncio
async def test_refresh_token_success(
    test_user: User,
    ac: AsyncClient,
    access_and_refresh_tokens_test_user: tuple,
):
    _, refresh = access_and_refresh_tokens_test_user
    cookies = {"resumes_token": refresh}
    response = await ac.get("/api/v1/refresh_token/", cookies=cookies)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "access_token_expire" in data


@pytest.mark.asyncio
async def test_refresh_token_invalid_token(ac: AsyncClient):
    cookies = {"resumes_token": "invalid_token"}
    response = await ac.get("/api/v1/refresh_token/", cookies=cookies)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token_user_not_found(
    ac: AsyncClient, access_and_refresh_tokens_invalid_user: tuple
):
    _, refresh = access_and_refresh_tokens_invalid_user
    cookies = {"resumes_token": refresh}
    response = await ac.get("/api/v1/refresh_token/", cookies=cookies)
    assert response.status_code == 400
