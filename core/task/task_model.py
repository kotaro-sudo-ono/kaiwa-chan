from dataclasses import dataclass
from typing import Any
import uuid


@dataclass
class Task:
    id: str
    type: str
    payload: Any
    status: str = "pending"

    @staticmethod
    def create(task_type: str, payload: Any):
        return Task(
            id=str(uuid.uuid4()),
            type=task_type,
            payload=payload,
            status="pending"
        )