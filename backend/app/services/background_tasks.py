"""Background tasks using Celery."""

import time

from celery import Celery

from app.config import settings

# Create Celery app
celery_app = Celery(
    "wire_tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)


@celery_app.task(name="process_wire_async")
def process_wire_async(wire_id: int) -> dict:
    """Process wire transfer asynchronously."""
    # Simulate wire processing (API calls, validation, etc.)
    time.sleep(5)

    # In real implementation, this would:
    # 1. Validate wire details
    # 2. Call external payment APIs
    # 3. Update wire status in database
    # 4. Send notifications
    # 5. Publish WebSocket event

    return {
        "wire_id": wire_id,
        "status": "completed",
        "message": "Wire processed successfully",
    }


@celery_app.task(name="send_wire_notification")
def send_wire_notification(wire_id: int, user_email: str, status: str) -> dict:
    """Send notification email for wire status change."""
    # Simulate email sending
    time.sleep(2)

    # In real implementation, this would send an actual email
    return {
        "wire_id": wire_id,
        "email": user_email,
        "status": status,
        "sent": True,
    }
