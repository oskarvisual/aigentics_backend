from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import ScheduledJobStatus
from app.jobs.queue import JobEnvelope, RedisJobQueue
from app.models.operation import ScheduledJob


class SchedulerService:
    def __init__(self, db: Session, queue: RedisJobQueue | None = None) -> None:
        self.db = db
        self.queue = queue or RedisJobQueue()

    def enqueue_due_jobs(self) -> int:
        now = datetime.now(UTC)
        jobs = list(
            self.db.scalars(
                select(ScheduledJob).where(
                    ScheduledJob.next_run_at.is_not(None), ScheduledJob.next_run_at <= now
                )
            )
        )
        for job in jobs:
            self.queue.enqueue(JobEnvelope(name=job.job_name, tenant_id=job.tenant_id, payload=job.payload))
            if job.interval_minutes:
                job.next_run_at = now + timedelta(minutes=job.interval_minutes)
            job.status = ScheduledJobStatus.QUEUED
        self.db.commit()
        return len(jobs)

