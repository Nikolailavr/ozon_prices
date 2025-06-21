import logging

from apps.parser import Parser
from apps.celery.celery_app import celery_app
from apps.celery.helper import CeleryHelper
from apps.celery.telegram import send_telegram_message
from celery.signals import task_success, task_failure

from core import settings
from core.database.schemas import UserRead

logger = logging.getLogger(__name__)

cel_helper = CeleryHelper()


@celery_app.task(
    bind=True,
    queue="parser",
    time_limit=300,
    soft_time_limit=180,
)
def parser_login(self):
    """Задача Celery для обработки чека"""
    try:
        result = Parser().login()
        return {"status": "success", "result": result}
    except Exception as e:
        logger.error(f"Общая ошибка")
        raise e
        # self.retry(exc=e, countdown=5, max_retries=2)


@celery_app.task(
    queue="parser",
    time_limit=300,
    soft_time_limit=180,
)
def parser_check(user_id: int):
    try:
        cel_helper.run(Parser().check(user_id=user_id))
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Общая ошибка")
        raise e


@celery_app.task(
    queue="parser",
    time_limit=300,
    soft_time_limit=280,
)
def parser_check_all():
    try:
        cel_helper.run(Parser().start_checking())
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Общая ошибка")
        raise e


# Успешное выполнение задачи
@task_success.connect
def task_success_handler(sender=None, result=None, **kwargs):
    logger.info(f"✅ Задача '{sender.name}' выполнена успешно")


# Ошибка при выполнении задачи
@task_failure.connect
def task_failure_handler(
    sender=None, task_id=None, exception=None, args=None, **kwargs
):
    logger.error(f"❌ Задача '{sender.name}' завершилась с ошибкой: {exception}")

    if sender.name == "apps.celery.tasks.parser_login":
        send_telegram_message.delay(
            {
                "chat_id": settings.telegram.admin_chat_id,
                "text": f"Задача '{sender.name}' завершилась с ошибкой: {exception}",
            }
        )
