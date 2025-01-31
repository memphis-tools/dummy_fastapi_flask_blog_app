"""The celery app definition"""

import os
from celery import Celery

try:
    from utils import get_secret
except ModuleNotFoundError:
    from app.packages.utils import get_secret


celery_app = Celery(
    name="project",
    backend=get_secret("/run/secrets/CELERY_RESULT_BACKEND"),
    broker=get_secret("/run/secrets/CELERY_BROKER_URL"),
    timezone=os.getenv("TIMEZONE"),
    result_expires=604800,
    include=["tasks"],
)
celery_app.conf.update(
    enable_utc=True,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_acks_on_failure_or_timeout=True,
    task_default_queue="celery",
    task_queues={
        'celery': {
            'exchange': 'celery',
            'exchange_type': 'direct',
            'binding_key': 'celery',
        },
    },
    task_routes={
        'tasks.some_task': {'queue': 'default'},
    },
)
