from flask import jsonify
from flask_openapi3 import APIBlueprint, Tag

from src.infrastructure.celery.celery_app import celery_app
from src.infrastructure.web.schemas.common.openapi_schemas import (
    ErrorResponseSchema,
    TaskIdPathSchema,
)
from src.infrastructure.web.schemas.common.task_schemas import (
    TaskResponseSchema,
    TaskStatsResponseSchema,
)
from src.infrastructure.web.utils.response import build_error_500_response


# Create blueprint with OpenAPI tags
task_tag = Tag(name="tasks", description="Celery tasks management")

task_bp = APIBlueprint(
    "tasks", __name__, url_prefix="/api/v1/tasks", abp_tags=[task_tag]
)


@task_bp.get(
    "/<task_id>",
    responses={
        200: TaskResponseSchema,
        500: ErrorResponseSchema,
    },
)
def get_task_status(path: TaskIdPathSchema):
    """Get the status of an async task."""
    try:
        task_id = path.task_id
        result = celery_app.AsyncResult(task_id)

        if result.state == "PENDING":
            response = TaskResponseSchema(
                task_id=task_id,
                state=result.state,
                status="Task is waiting to be processed",
            )
        elif result.state == "PROGRESS":
            response = TaskResponseSchema(
                task_id=task_id,
                state=result.state,
                current=result.info.get("current", 0),
                total=result.info.get("total", 1),
                status=result.info.get("status", ""),
            )
        elif result.state == "SUCCESS":
            response = TaskResponseSchema(
                task_id=task_id,
                state=result.state,
                result=result.result,
                status="Task completed successfully",
            )
        else:
            # FAILURE or other states
            response = TaskResponseSchema(
                task_id=task_id,
                state=result.state,
                error=str(result.info),
                status="Task failed",
            )

        return jsonify(response.model_dump()), 200

    except Exception:
        return build_error_500_response()


@task_bp.post(
    "/<task_id>/cancel",
    responses={
        200: {"description": "Task cancellation requested"},
        500: ErrorResponseSchema,
    },
)
def cancel_task(path: TaskIdPathSchema):
    """Cancel a running task."""
    try:
        task_id = path.task_id
        celery_app.control.revoke(task_id, terminate=True)

        return jsonify(
            {
                "task_id": task_id,
                "message": "Task cancellation requested",
                "status": "cancelled",
            },
        ), 200

    except Exception:
        return build_error_500_response()


@task_bp.get(
    "/stats",
    responses={
        200: TaskStatsResponseSchema,
        500: ErrorResponseSchema,
    },
)
def get_task_stats():
    """Get Celery task statistics."""
    try:
        # Get active tasks
        active_tasks = celery_app.control.inspect().active()

        # Get scheduled tasks
        scheduled_tasks = celery_app.control.inspect().scheduled()

        # Get worker stats
        worker_stats = celery_app.control.inspect().stats()

        # Count tasks by state
        total_active = sum(len(tasks) for tasks in (active_tasks or {}).values())
        total_scheduled = sum(len(tasks) for tasks in (scheduled_tasks or {}).values())

        response = TaskStatsResponseSchema(
            active_tasks=total_active,
            scheduled_tasks=total_scheduled,
            workers=list((worker_stats or {}).keys()),
            worker_count=len(worker_stats or {}),
            queues=["default", "firewall", "policy", "rule", "notification"],
            task_details={
                "active": active_tasks,
                "scheduled": scheduled_tasks,
                "worker_stats": worker_stats,
            },
        )

        return jsonify(response.model_dump()), 200

    except Exception:
        return build_error_500_response()
