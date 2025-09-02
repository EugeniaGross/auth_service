import logging
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status

from auth.dependiences import user_service
from auth.exceptions import UserNotFoundError, VerifyPasswordError
from auth.schemes import JWTAccessToken, UserRequestScheme, UserResponseScheme
from auth.services import UserService
from settings import settings
from utils.tokens import JWTTokenService

router = APIRouter(prefix="/api/v1", tags=["Auth"])


@router.post(
    "/registration/",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponseScheme,
)
async def create_user(
    user: UserRequestScheme,
    user_service: UserService = Depends(user_service),
):
    """
    Регистрация нового пользователя.
    Проверяет, существует ли пользователь с таким email.
    Хэширует пароль и сохраняет пользователя в базе данных.
    Args:
        user (UserRequestScheme): Данные пользователя (email, password).
        user_service (UserService): Сервис для работы с пользователями.
    Raises:
        HTTPException: Если пользователь с таким email уже существует.
    Returns:
        UserResponseScheme: Данные пользователя.
    """
    if await user_service.get_one_by_email(email=user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже зарегестрирован",
        )
    user = await user_service.add_one(user)
    return user


@router.post("/login/")
async def login(
    response: Response,
    user: UserRequestScheme,
    user_service: UserService = Depends(user_service),
    token_service: JWTTokenService = Depends(JWTTokenService),
):
    """
    Аутентификация пользователя.
    - Проверяет корректность email и пароля.
    - Создаёт access и refresh токены.
    - Сохраняет refresh token в cookie `resumes_token`.
    Args:
        response (Response): Объект FastAPI Response для установки cookie.
        user (UserRequestScheme): Данные пользователя.
        user_service (UserService): Сервис пользователей.
        token_service (JWTTokenService): Сервис генерации JWT токенов.
    Raises:
        HTTPException: Если email или пароль некорректны.
    Returns:
        JWTAccessToken: Access токен с временем жизни.
    """
    try:
        user = await user_service.authenticate_user(user)
    except (UserNotFoundError, VerifyPasswordError) as e:
        logging.error(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Некорректный email или пароль",
        )

    access_token, refresh_token = (
        token_service.create_access_and_refresh_tokens({"id": user.id})
    )

    response.set_cookie(
        key="resumes_token",
        value=refresh_token,
        httponly=True,
        expires=datetime.now(
            timezone.utc
        ) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        ),
        secure=True,
    )

    return JWTAccessToken(
        access_token=access_token,
        access_token_expire=datetime.now(
            timezone.utc
        ) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        ),
    )


@router.post("/logout/")
async def logout(response: Response):
    """
    Выход пользователя из системы.
    Удаляет cookie с refresh token `resumes_token`.
    Args:
        response (Response): Объект FastAPI Response для удаления cookie.
    Returns:
        None
    """
    response.delete_cookie("resumes_token", httponly=True, secure=True)
    return


@router.get("/refresh_token/")
async def refresh_token(
    response: Response,
    resumes_token: str = Cookie(default=None),
    user_service: UserService = Depends(user_service),
    token_service: JWTTokenService = Depends(JWTTokenService),
):
    """
    Обновление access и refresh токенов.
    - Проверяет валидность refresh token из cookie.
    - Генерирует новые access и refresh токены.
    - Сохраняет новый refresh token в cookie.
    Args:
        response (Response): Объект FastAPI Response для установки cookie.
        resumes_token (str): Refresh token из cookie.
        user_service (UserService): Сервис пользователей.
        token_service (JWTTokenService): Сервис генерации JWT токенов.
    Returns:
        JWTAccessToken: Новый access токен.
    Raises:
        HTTPException: Если refresh token не валиден или пользователь не найден.
    """
    decode_token = token_service.decode_jwt_token(resumes_token)
    if decode_token is None or decode_token.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="refresh_token не валиден",
        )

    user = await user_service.get_one(id=decode_token["id"])
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь не зарегестрирован",
        )

    access_token, refresh_token = (
        token_service.create_access_and_refresh_tokens({"id": user.id})
    )

    response.set_cookie(
        key="resumes_token",
        value=refresh_token,
        httponly=True,
        expires=datetime.now(
            timezone.utc
        ) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        ),
        secure=True,
    )

    return JWTAccessToken(
        access_token=access_token,
        access_token_expire=datetime.now(
            timezone.utc
        ) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        ),
    )


@router.get("/jwt.key")
def get_public_key():
    """
    Получение публичного ключа для верификации JWT.

    Returns:
        dict: Словарь с публичным ключом {"public_key": str}.
    """
    return {"public_key": settings.PUBLIC_KEY}
