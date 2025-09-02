from abc import ABC, abstractmethod
from typing import Optional

from sqlalchemy import select

from auth.models import User
from database import async_session


class UsersAbstractRepository(ABC):
    """
    Абстрактный репозиторий для работы с пользователями.

    Определяет базовые методы для:
    - добавления пользователя,
    - получения пользователя по email.

    Конкретные реализации должны реализовать все методы.
    """

    @abstractmethod
    async def add_one(self, data: dict) -> User:
        """
        Добавляет нового пользователя.
        Args:
            data (dict): Данные для создания пользователя.
        Returns:
            User: Созданный пользователь.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_one_by_email(self, email: str) -> Optional[User]:
        """
        Получает пользователя по email.
        Args:
            email (str): Электронная почта пользователя.
        Returns:
            Optional[User]: Пользователь или None, если не найден.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_one(self, id: int) -> Optional[User]:
        """
        Получает пользователя по его идентификатору.
        Args:
            id (int): Идентификатор пользователя.
        Returns:
            Optional[User]: Пользователь или None, если не найден.
        """
        raise NotImplementedError


class UsersPostgreSQLRepository(UsersAbstractRepository):
    """
    Репозиторий пользователей с использованием PostgreSQL и SQLAlchemy Async.
    """

    @staticmethod
    async def add_one(data: dict) -> User:
        async with async_session() as session:
            user = User(**data)
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user

    @staticmethod
    async def get_one_by_email(email: str) -> Optional[User]:
        async with async_session() as session:
            query = select(User).where(User.email == email)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @staticmethod
    async def get_one(id: int) -> Optional[User]:
        async with async_session() as session:
            result = await session.get(User, id)
            return result
