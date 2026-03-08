"""
Task management module for async contract auditing.
"""
import uuid
from typing import Dict, Optional
from datetime import datetime
from enum import Enum
from core.logger import get_logger


class TaskStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskManager:
    """In-memory task manager for async audit processing."""

    def __init__(self):
        self.tasks: Dict[str, Dict] = {}
        self.logger = get_logger(self.__class__.__name__)

    def create_task(self, contract_name: str) -> str:
        """Create a new audit task."""
        task_id = str(uuid.uuid4())
        self.tasks[task_id] = {
            "task_id": task_id,
            "contract_name": contract_name,
            "status": TaskStatus.PENDING.value,
            "created_at": datetime.now().isoformat(),
            "result": None,
            "error": None,
            "progress": 0,
        }
        self.logger.info(f"Created task {task_id} for {contract_name}")
        return task_id

    def get_task(self, task_id: str) -> Optional[Dict]:
        """Get task by ID."""
        return self.tasks.get(task_id)

    def update_task(
        self,
        task_id: str,
        status: str,
        result: Optional[Dict] = None,
        error: Optional[str] = None,
        progress: Optional[int] = None
    ):
        """Update task status and result."""
        if task_id in self.tasks:
            self.tasks[task_id]["status"] = status
            if result is not None:
                self.tasks[task_id]["result"] = result
            if error is not None:
                self.tasks[task_id]["error"] = error
            if progress is not None:
                self.tasks[task_id]["progress"] = progress
            self.logger.info(f"Updated task {task_id}: {status}")

    def list_tasks(self, limit: int = 50) -> list:
        """List recent tasks."""
        tasks = sorted(
            self.tasks.values(),
            key=lambda x: x.get("created_at", ""),
            reverse=True
        )
        return tasks[:limit]


# Global task manager instance
task_manager = TaskManager()
