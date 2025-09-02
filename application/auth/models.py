from pydantic import EmailStr
from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    """
    ORM-модель пользователя для хранения в базе данных.
    Атрибуты:
        id (int): Уникальный идентификатор пользователя (Primary Key).
        email (EmailStr): Электронная почта пользователя (уникальное поле).
        hash_password (str): Хэшированный пароль пользователя.
    """

    __tablename__ = "users"
    __table_args__ = {"extend_existing": True}
    id: int = Field(default=None, primary_key=True)
    email: EmailStr = Field(unique=True)
    hash_password: str
