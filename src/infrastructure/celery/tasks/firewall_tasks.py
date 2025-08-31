import logging
import time
from datetime import UTC, datetime

from src.domain.use_cases.firewall.get_firewall_use_case import GetFirewallUseCase
from src.infrastructure.celery.celery_app import celery_app
from src.infrastructure.database.connection import get_db_session
from src.infrastructure.repositories.firewall.sqlalchemy_firewall_repository import (
    SQLAlchemyFirewallRepository,
)


logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="fireflow.tasks.firewall.health_check")
def firewall_health_check_task(self, firewall_id: int):
    """
    Async task to perform health check on a firewall.

    Args:
        firewall_id: ID of the firewall to check

    Returns:
        dict: Health check results
    """
    try:
        logger.info(f"Starting health check for firewall {firewall_id}")

        # Simulate health check process
        time.sleep(2)  # Simulate network check

        with get_db_session() as session:
            repository = SQLAlchemyFirewallRepository(session)
            get_use_case = GetFirewallUseCase(repository)

            firewall = get_use_case.execute(firewall_id)

            # Simulate ping/connectivity check
            health_status = "healthy" if firewall.status == "active" else "unhealthy"

            result = {
                "firewall_id": firewall_id,
                "name": firewall.name,
                "ip_address": firewall.ip_address,
                "status": health_status,
                "checked_at": datetime.now(UTC).isoformat(),
                "response_time_ms": 150,  # Simulated
            }

            logger.info(
                f"Health check completed for firewall {firewall_id}: {health_status}",
            )
            return result

    except Exception as exc:
        logger.exception(f"Health check failed for firewall {firewall_id}")
        self.retry(exc=exc, countdown=60, max_retries=3)


@celery_app.task(bind=True, name="firewall.tasks.firewall.backup_configuration")
def backup_firewall_configuration_task(self, firewall_id: int):
    """
    Async task to backup firewall configuration.

    Args:
        firewall_id: ID of the firewall to backup

    Returns:
        dict: Backup results
    """
    try:
        logger.info(f"Starting configuration backup for firewall {firewall_id}")

        with get_db_session() as session:
            repository = SQLAlchemyFirewallRepository(session)
            get_use_case = GetFirewallUseCase(repository)

            firewall = get_use_case.execute(firewall_id)

            # Simulate backup process
            time.sleep(3)  # Simulate configuration retrieval

            backup_data = {
                "firewall_id": firewall_id,
                "name": firewall.name,
                "ip_address": firewall.ip_address,
                "port": firewall.port,
                "status": firewall.status,
                "backed_up_at": datetime.now(UTC).isoformat(),
                "backup_size_kb": 245,  # Simulated
                "backup_location": f"/backups/firewall_{firewall_id}_{int(time.time())}.json",
            }

            logger.info(f"Configuration backup completed for firewall {firewall_id}")
            return backup_data

    except Exception as exc:
        logger.exception(f"Configuration backup failed for firewall {firewall_id}")
        self.retry(exc=exc, countdown=120, max_retries=2)


@celery_app.task(name="fireflow.tasks.firewall.batch_health_check")
def batch_firewall_health_check_task(firewall_ids: list[int]):
    """
    Async task to perform health check on multiple firewalls.

    Args:
        firewall_ids: List of firewall IDs to check

    Returns:
        dict: Batch health check results
    """
    try:
        logger.info(f"Starting batch health check for {len(firewall_ids)} firewalls")

        results = []
        for firewall_id in firewall_ids:
            # Trigger individual health check tasks
            task_result = firewall_health_check_task.delay(firewall_id)
            results.append(
                {
                    "firewall_id": firewall_id,
                    "task_id": task_result.id,
                    "status": "queued",
                },
            )

        batch_result = {
            "batch_id": f"batch_{int(time.time())}",
            "total_firewalls": len(firewall_ids),
            "started_at": datetime.now(UTC).isoformat(),
            "individual_tasks": results,
        }

        logger.info(f"Batch health check initiated for {len(firewall_ids)} firewalls")
    except Exception:
        logger.exception("Batch health check failed")
        raise
    else:
        return batch_result
