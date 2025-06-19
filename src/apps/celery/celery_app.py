from celery import Celery

from core import settings

celery_app = Celery(
    "apps.celery.celery_app",
    broker=settings.celery.BROKER_URL,
    backend=settings.celery.RESULT_BACKEND,
    include=["apps.celery.parser", "apps.celery.telegram"],
    broker_connection_retry_on_startup=True,
    broker_transport_options={
        "visibility_timeout": 3600,
        "socket_timeout": 10,  # Таймаут на уровне сокета
        "socket_connect_timeout": 5,  # Таймаут на подключение
    },
)

celery_app.conf.update(
    task_track_started=True,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)
