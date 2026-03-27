from __future__ import annotations

import socketio
from fastapi import FastAPI

from app.core.config import get_settings

settings = get_settings()
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins=settings.cors_origins)


@sio.event
async def connect(sid: str, environ: dict, auth: dict | None) -> None:  # noqa: ARG001
    await sio.emit("system.connected", {"sid": sid}, to=sid)


@sio.event
async def join_workspace(sid: str, data: dict) -> None:
    tenant_id = data["tenant_id"]
    await sio.enter_room(sid, f"tenant:{tenant_id}")


@sio.event
async def join_conversation(sid: str, data: dict) -> None:
    conversation_id = data["conversation_id"]
    await sio.enter_room(sid, f"conversation:{conversation_id}")


def create_socket_app(fastapi_app: FastAPI) -> socketio.ASGIApp:
    return socketio.ASGIApp(sio, fastapi_app, socketio_path=settings.socket_io_path)


class RealtimePublisher:
    async def publish_workspace_event(self, tenant_id: str, event: str, payload: dict) -> None:
        await sio.emit(event, payload, room=f"tenant:{tenant_id}")

    async def publish_conversation_event(
        self, conversation_id: str, event: str, payload: dict
    ) -> None:
        await sio.emit(event, payload, room=f"conversation:{conversation_id}")
