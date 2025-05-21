from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio
from src.bot.handlers import register_all_handlers
from core import settings

bot = Bot(token=settings.telegram.token, parse_mode="HTML")
dp = Dispatcher(storage=MemoryStorage())


async def start_bot():
    # Регистрация обработчиков
    register_all_handlers(dp)

    # Запуск поллинга
    await dp.start_polling(bot, skip_updates=True)


def run():
    asyncio.run(start_bot())


if __name__ == "__main__":
    run()
