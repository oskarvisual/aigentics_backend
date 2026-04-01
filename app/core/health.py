from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from time import perf_counter

from botocore.config import Config
from qdrant_client import QdrantClient
from redis import Redis
from sqlalchemy import text

from app.core.config import get_settings
from app.db.session import engine


@dataclass
class DependencyCheckResult:
    name: str
    status: str
    latency_ms: int
    detail: str

    def to_dict(self) -> dict[str, str | int]:
        return {
            "status": self.status,
            "latency_ms": self.latency_ms,
            "detail": self.detail,
        }


def _timed_check(name: str, check: callable) -> DependencyCheckResult:
    started_at = perf_counter()
    try:
        detail = check()
        elapsed_ms = int((perf_counter() - started_at) * 1000)
        return DependencyCheckResult(
            name=name,
            status="ok",
            latency_ms=elapsed_ms,
            detail=detail,
        )
    except Exception as exc:  # noqa: BLE001
        elapsed_ms = int((perf_counter() - started_at) * 1000)
        return DependencyCheckResult(
            name=name,
            status="error",
            latency_ms=elapsed_ms,
            detail=str(exc),
        )


def _check_mysql() -> str:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return "MySQL reachable"


def _check_redis() -> str:
    client = Redis.from_url(get_settings().redis_url, socket_connect_timeout=2, socket_timeout=2)
    response = client.ping()
    if response is not True:
        raise RuntimeError("Redis ping returned a non-success response.")
    return "Redis reachable"


def _check_qdrant() -> str:
    settings = get_settings()
    client = QdrantClient(
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key,
        timeout=3,
    )
    collections = client.get_collections().collections
    return f"Qdrant reachable ({len(collections)} collections visible)"


def _check_object_storage() -> str:
    settings = get_settings()
    from boto3 import client as boto3_client

    s3_client = boto3_client(
        "s3",
        endpoint_url=settings.s3_endpoint,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
        region_name=settings.s3_region,
        config=Config(signature_version="s3v4", connect_timeout=3, read_timeout=3),
    )
    s3_client.head_bucket(Bucket=settings.s3_bucket)
    return f"Object storage reachable (bucket: {settings.s3_bucket})"


def _check_provider_config(name: str, configured: bool) -> DependencyCheckResult:
    return DependencyCheckResult(
        name=name,
        status="ok" if configured else "error",
        latency_ms=0,
        detail=f"{name} configured" if configured else f"{name} missing configuration",
    )


def compute_overall_status(results: list[DependencyCheckResult]) -> str:
    if all(result.status == "ok" for result in results):
        return "ok"
    if all(result.status == "error" for result in results):
        return "error"
    return "degraded"


def run_health_checks() -> dict:
    settings = get_settings()
    dependency_results = [
        _timed_check("mysql", _check_mysql),
        _timed_check("redis", _check_redis),
        _timed_check("qdrant", _check_qdrant),
        _timed_check("object_storage", _check_object_storage),
        _check_provider_config("openai_api", configured=bool(settings.openai_api_key)),
        _check_provider_config("google_api", configured=bool(settings.google_api_key)),
    ]
    overall_status = compute_overall_status(dependency_results)
    return {
        "status": overall_status,
        "checked_at": datetime.now(UTC).isoformat(),
        "services": {result.name: result.to_dict() for result in dependency_results},
    }
