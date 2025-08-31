"""Task-related Pydantic schemas for OpenAPI documentation."""

from typing import Any

from pydantic import BaseModel, Field


class TaskResponseSchema(BaseModel):
    """Schema for task status responses."""

    task_id: str = Field(description="Task ID")
    state: str = Field(description="Task State")
    current: int | None = Field(default=None, description="Current Progress")
    total: int | None = Field(default=None, description="Total Progress")
    error: str | None = Field(default=None, description="Task Error")
    result: Any | None = Field(default=None, description="Task Result")
    status: str | None = Field(default=None, description="Task Status")


class TaskStatsResponseSchema(BaseModel):
    """Schema for Celery task statistics."""

    active_tasks: int = Field(description="Number of active tasks")
    scheduled_tasks: int = Field(description="Number of scheduled tasks")
    workers: list[str] = Field(description="List of worker names")
    worker_count: int = Field(description="Number of active workers")
    queues: list[str] = Field(description="List of queue names")
    task_details: dict = Field(description="Detailed task information")
