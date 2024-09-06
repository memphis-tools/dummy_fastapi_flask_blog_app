"""The celery app definition"""

import os
from celery import Celery

celery_app = Celery(
    name="project",
    backend=os.getenv("CELERY_RESULT_BACKEND"),
    broker=os.getenv("CELERY_BROKER_URL"),
    timezone=os.getenv("TIMEZONE"),
    include=["tasks"],
)
celery_app.conf.update(
    enable_utc=True, task_serializer="json", result_serializer="json"
)
