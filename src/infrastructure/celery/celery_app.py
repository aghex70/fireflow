import logging

from celery import Celery
from kombu import Queue

from src.infrastructure.config.settings import get_settings


logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()

# Create Celery app
celery_app = Celery("fireflow")

# Configure Celery
celery_app.conf.update(
    broker_url=settings.celery.broker_url,
    result_backend=settings.celery.result_backend,
    task_serializer=settings.celery.task_serializer,
    accept_content=["json"],
    result_serializer=settings.celery.result_serializer,
    timezone=settings.celery.timezone,
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    task_routes={
        "fireflow.tasks.firewall.*": {"queue": "firewall"},
        "fireflow.tasks.policy.*": {"queue": "policy"},
        "fireflow.tasks.rule.*": {"queue": "rule"},
        "fireflow.tasks.notification.*": {"queue": "notification"},
    },
    task_default_queue="default",
    task_queues=(
        Queue("default"),
        Queue("firewall"),
        Queue("policy"),
        Queue("rule"),
        Queue("notification"),
    ),
)

# Auto-discover tasks
celery_app.autodiscover_tasks(["infrastructure.celery.tasks"])


def make_celery(app=None):
    """Create Celery app with Flask context."""
    if app:
        # Update task base classes to work with Flask app context
        class ContextTask(celery_app.Task):
            """Make celery tasks work with Flask app context."""

            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return self.run(*args, **kwargs)

        celery_app.Task = ContextTask

    return celery_app
