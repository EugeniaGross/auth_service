from datetime import datetime, timezone, timedelta
from typing import Tuple, Optional, Dict, Any

from jose import JWTError, jwt
from settings import settings


class JWTTokenService:
    """
    Сервис для генерации и валидации JWT токенов.
    """

    @classmethod
    def create_access_and_refresh_tokens(cls, data: dict) -> Tuple[str, str]:
        """
        Создаёт пару токенов: access и refresh.
        Args:
            data (dict): Данные, которые будут добпавлены в payload токена.
        Returns:
            Tuple[str, str]: Кортеж, который содержит access_token и refresh_token.
        """
        access_token = cls._create_jwt_token(
            data,
            "access",
            settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        )
        refresh_token = cls._create_jwt_token(
            data,
            "refresh",
            settings.REFRESH_TOKEN_EXPIRE_DAYS,
        )
        return access_token, refresh_token

    @staticmethod
    def _create_jwt_token(data: dict, type: str, token_expire: int) -> str:
        """
        Создаёт JWT токен определённого типа.
        Args:
            data (dict): Данные для payload.
            type (str): Тип токена.
            token_expire (int): Время жизни токена.
        Returns:
            str: Сгенерированный JWT токен.
        """
        if type == "access":
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=token_expire
            )
        elif type == "refresh":
            expire = datetime.now(timezone.utc) + timedelta(days=token_expire)
        else:
            raise ValueError(
                "Неверный тип токена. Ожидается 'access' или 'refresh'."
            )

        payload = data.copy()
        payload.update({"exp": expire, "type": type})

        token = jwt.encode(
            payload, settings.PRIVATE_KEY, algorithm=settings.JWT_ALGORITHM
        )
        return token

    @staticmethod
    def decode_jwt_token(token: str) -> Optional[Dict[str, Any]]:
        """
        Декодирует и проверяет JWT токен.
        Args:
            token (str): JWT токен.
        Returns:
            Optional[Dict[str, Any]]:
                - словарь с расшифрованными данными, если токен валиден;
                - None, если токен невалидный или не соответствует схеме.
        """
        try:
            decode_token = jwt.decode(
                token,
                settings.PUBLIC_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
        except (JWTError, AttributeError):
            return None

        if set(decode_token.keys()) != {"id", "exp", "type"}:
            return None

        return decode_token
