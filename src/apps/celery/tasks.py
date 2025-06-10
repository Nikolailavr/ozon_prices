import logging

from apps.parser.parser import Parser
from apps.celery.celery_app import celery_app
from apps.celery.helper import CeleryHelper
from celery.signals import task_success, task_failure

logger = logging.getLogger(__name__)

cel_helper = CeleryHelper()


@celery_app.task(bind=True)
def parser_login(self):
    """Задача Celery для обработки чека"""
    try:
        parser = Parser()
        result = parser.login()
        return {"status": "success", "result": result}
    except Exception as e:
        logger.error(f"Общая ошибка")
        raise e
        # self.retry(exc=e, countdown=5, max_retries=2)


@celery_app.task()
def parser_check(url: str):
    try:
        cel_helper.run(Parser().check(url))
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

    if sender.name == "apps.celery.tasks.cmd_login" and args:
        ...
