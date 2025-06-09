import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from apps.bot.handlers import register_all_handlers
from core import settings

logger = logging.getLogger(__name__)

bot = Bot(token=settings.telegram.token)
dp = Dispatcher(storage=MemoryStorage())


async def send_msg(
    chat_id: int,
    text: str,
):
    await bot.send_message(chat_id=chat_id, text=text)


async def start_bot():
    # Регистрация обработчиков
    register_all_handlers(dp)

    # Запуск поллинга
    await dp.start_polling(bot, skip_updates=True)
