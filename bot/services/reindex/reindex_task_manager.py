import asyncio
from dataclasses import (
    dataclass,
    field,
)
from datetime import (
    datetime,
    timezone,
)
from typing import (
    List,
    Optional,
)
import uuid


@dataclass
class ReindexTaskStatus:
    task_id: str
    target: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    series_name: Optional[str] = None
    episodes_processed: int = 0
    documents_indexed: int = 0
    errors: List[str] = field(default_factory=list)
    error: Optional[str] = None


class ReindexTaskManager:
    def __init__(self) -> None:
        self._tasks: dict[str, ReindexTaskStatus] = {}
        self._lock = asyncio.Lock()

    async def create_task(self, target: str) -> str:
        task_id = uuid.uuid4().hex[:16]
        task = ReindexTaskStatus(
            task_id=task_id,
            target=target,
            status="pending",
            created_at=datetime.now(timezone.utc),
        )
        async with self._lock:
            self._tasks[task_id] = task
        return task_id

    async def start_task(self, task_id: str) -> None:
        async with self._lock:
            task = self._tasks.get(task_id)
            if task:
                task.status = "running"

    async def complete_task(
        self,
        task_id: str,
        series_name: str,
        episodes_processed: int,
        documents_indexed: int,
        errors: Optional[List[str]] = None,
    ) -> None:
        async with self._lock:
            task = self._tasks.get(task_id)
            if task:
                task.status = "completed"
                task.completed_at = datetime.now(timezone.utc)
                task.series_name = series_name
                task.episodes_processed = episodes_processed
                task.documents_indexed = documents_indexed
                task.errors = errors or []

    async def complete_task_multi(
        self,
        task_id: str,
        total_episodes: int,
        total_documents: int,
        errors: Optional[List[str]] = None,
    ) -> None:
        async with self._lock:
            task = self._tasks.get(task_id)
            if task:
                task.status = "completed"
                task.completed_at = datetime.now(timezone.utc)
                task.series_name = task.target
                task.episodes_processed = total_episodes
                task.documents_indexed = total_documents
                task.errors = errors or []

    async def fail_task(self, task_id: str, error: str) -> None:
        async with self._lock:
            task = self._tasks.get(task_id)
            if task:
                task.status = "failed"
                task.completed_at = datetime.now(timezone.utc)
                task.error = error

    async def get_status(self, task_id: str) -> Optional[ReindexTaskStatus]:
        async with self._lock:
            return self._tasks.get(task_id)


task_manager = ReindexTaskManager()
