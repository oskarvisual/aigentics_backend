from collections.abc import Callable

from app.jobs.queue import JobEnvelope, RedisJobQueue


class JobWorker:
    def __init__(self, handlers: dict[str, Callable[[JobEnvelope], None]]) -> None:
        self.handlers = handlers
        self.queue = RedisJobQueue()

    def run_once(self) -> bool:
        job = self.queue.dequeue()
        if job is None:
            return False
        handler = self.handlers.get(job.name)
        if handler is None:
            return False
        handler(job)
        return True

