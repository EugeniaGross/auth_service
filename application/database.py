from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)

from settings import settings

if settings.TESTING:
    async_engine = create_async_engine(
        settings.DB_URL_testing, echo=False, poolclass=NullPool
    )
else:
    async_engine = create_async_engine(
        settings.DB_URL,
        pool_recycle=3600,
        echo=True,
        future=True,
    )

async_session = async_sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)
