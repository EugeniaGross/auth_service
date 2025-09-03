from pathlib import Path
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from auth.routers import router as auth_router
from settings import settings

if not settings.TESTING:
    from uvicorn.workers import UvicornWorker

    class BackendUvicornWorker(UvicornWorker):
        """
        Воркер с настроенным логгированием
        """

        CONFIG_KWARGS = {
            "log_config": (
                f"{str(Path(__file__).resolve().parent.parent) + os.sep}logging.yaml"
            ),
        }


app = FastAPI(
    openapi_url="/api/v1/auth/openapi.json"
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=(
        settings.ALLOWED_HOSTS
        if not settings.TESTING
        else settings.TEST_ALLOWED_HOSTS
    ),
)

origins = settings.ORIGINS if not settings.TESTING else settings.TEST_ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
