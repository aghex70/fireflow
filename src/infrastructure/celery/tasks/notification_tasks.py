import logging
import time
from datetime import datetime, timezone

from src.infrastructure.celery.celery_app import celery_app


logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="fireflow.tasks.notification.send_email")
def send_email_notification_task(
    self,
    to_email: str,
    subject: str,
    _message: str,
    notification_type: str = "info",
):
    """
    Async task to send email notifications.

    Args:
        to_email: Recipient email address
        subject: Email subject
        message: Email message body
        notification_type: Type of notification (info, warning, error)

    Returns:
        dict: Email sending results
    """
    try:
        logger.info(f"Sending email notification to {to_email}")

        # Simulate email sending process
        time.sleep(1)  # Simulate SMTP connection and sending

        result = {
            "to_email": to_email,
            "subject": subject,
            "notification_type": notification_type,
            "sent_at": datetime.now(timezone.utc).isoformat(),
            "status": "sent",
            "message_id": f"msg_{int(time.time())}_{hash(to_email) % 10000}",
        }

        logger.info(f"Email notification sent successfully to {to_email}")
    except Exception as exc:
        logger.exception(f"Failed to send email to {to_email}")
        self.retry(exc=exc, countdown=30, max_retries=3)
    else:
        return result


@celery_app.task(name="fireflow.tasks.notification.send_webhook")
def send_webhook_notification_task(webhook_url: str, payload: dict, event_type: str):
    """
    Async task to send webhook notifications.

    Args:
        webhook_url: Webhook endpoint URL
        payload: Data to send in webhook
        event_type: Type of event (firewall_created, policy_updated, etc.)

    Returns:
        dict: Webhook sending results
    """
    try:
        logger.info(f"Sending webhook notification to {webhook_url}")

        # Simulate webhook sending process
        time.sleep(0.5)  # Simulate HTTP request

        result = {
            "webhook_url": webhook_url,
            "event_type": event_type,
            "payload_size": len(str(payload)),
            "sent_at": datetime.now(timezone.utc).isoformat(),
            "status": "delivered",
            "response_code": 200,
            "response_time_ms": 150,
        }

        logger.info(f"Webhook notification sent successfully to {webhook_url}")
    except Exception:
        logger.exception(f"Failed to send webhook to {webhook_url}")
        raise
    else:
        return result
