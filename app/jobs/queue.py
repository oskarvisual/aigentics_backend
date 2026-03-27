from __future__ import annotations

import json
from datetime import UTC, datetime

from pydantic import BaseModel, Field
from redis import Redis

from app.core.config import get_settings


class JobEnvelope(BaseModel):
    name: str
    tenant_id: str | None = None
    payload: dict = Field(default_factory=dict)
    enqueued_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class RedisJobQueue:
    def __init__(self, queue_name: str = "aigentics:jobs") -> None:
        self.queue_name = queue_name
        self.redis = Redis.from_url(get_settings().redis_url, decode_responses=True)

    def enqueue(self, job: JobEnvelope) -> None:
        self.redis.rpush(self.queue_name, job.model_dump_json())

    def dequeue(self, timeout: int = 5) -> JobEnvelope | None:
        item = self.redis.blpop(self.queue_name, timeout=timeout)
        if item is None:
            return None
        _, raw = item
        return JobEnvelope.model_validate(json.loads(raw))

