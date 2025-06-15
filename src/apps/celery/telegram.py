import logging

from apps.celery.celery_app import celery_app
from apps.celery.helper import CeleryHelper


from core.database.schemas import TelegramMessage

logger = logging.getLogger(__name__)

cel_helper = CeleryHelper()


@celery_app.task(queue="telegram")
def send_telegram_message(data: dict):
    try:
        from apps.bot import send_msg

        msg = TelegramMessage.model_validate(data)

        cel_helper.run(send_msg(chat_id=msg.chat_id, text=msg.text))
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Общая ошибка")
        raise e
