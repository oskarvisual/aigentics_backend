from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import get_settings
from app.realtime.socket import create_socket_app

settings = get_settings()

fastapi_app = FastAPI(
    title="Aigentics Backend",
    version="0.1.0",
    openapi_url=f"{settings.api_v1_prefix}/openapi.json",
)

fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
fastapi_app.include_router(api_router, prefix=settings.api_v1_prefix)


@fastapi_app.get("/health", tags=["health"])
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


app = create_socket_app(fastapi_app)
