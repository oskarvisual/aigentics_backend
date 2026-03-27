from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4

import jwt
from pwdlib import PasswordHash

from app.core.config import get_settings

password_hasher = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return password_hasher.verify(password, password_hash)


def create_access_token(subject: str, tenant_id: str | None = None) -> str:
    settings = get_settings()
    expire_at = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)
    payload: dict[str, Any] = {"sub": subject, "type": "access", "exp": expire_at}
    if tenant_id:
        payload["tenant_id"] = tenant_id
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def create_refresh_token(subject: str, session_id: str) -> tuple[str, datetime]:
    settings = get_settings()
    expire_at = datetime.now(UTC) + timedelta(days=settings.refresh_token_expire_days)
    payload = {"sub": subject, "type": "refresh", "sid": session_id, "exp": expire_at}
    return jwt.encode(payload, settings.jwt_refresh_secret, algorithm="HS256"), expire_at


def decode_access_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    return jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])


def decode_refresh_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    return jwt.decode(token, settings.jwt_refresh_secret, algorithms=["HS256"])


def new_id() -> str:
    return str(uuid4())

