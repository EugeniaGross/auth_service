import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Настройки сервиса
    """

    model_config = SettingsConfigDict(
        env_file=f"{str(Path(__file__).resolve().parent.parent) + os.sep}.env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    JWT_ALGORITHM: str
    PRIVATE_KEY_PATH: str
    PUBLIC_KEY_PATH: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    POSTGRES_PORT: int
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    ALLOWED_HOSTS_STRING: str
    ORIGINS_STRING: str
    TEST_ALLOWED_HOSTS_STRING: str
    TEST_ORIGINS_STRING: str
    TESTING: bool = False

    @property
    def ALLOWED_HOSTS(self):
        return self.ALLOWED_HOSTS_STRING.split(",")

    @property
    def ORIGINS(self):
        return self.ORIGINS_STRING.split(",")

    @property
    def TEST_ALLOWED_HOSTS(self):
        return self.TEST_ALLOWED_HOSTS_STRING.split(",")

    @property
    def TEST_ORIGINS(self):
        return self.TEST_ORIGINS_STRING.split(",")

    @property
    def DB_URL(self):
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def DB_URL_testing(self):
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/test"
        )

    @property
    def PRIVATE_KEY(self):
        with open(self.PRIVATE_KEY_PATH) as file:
            return file.read()

    @property
    def PUBLIC_KEY(self):
        with open(self.PUBLIC_KEY_PATH) as file:
            return file.read()


settings = Settings()
