from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio
from src.bot.handlers import register_all_handlers
from core import settings


async def main():
    # Инициализация бота и диспетчера
    bot = Bot(token=settings.telegram.token, parse_mode="HTML")
    dp = Dispatcher(storage=MemoryStorage())

    # Регистрация обработчиков
    register_all_handlers(dp)

    # Запуск поллинга
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    asyncio.run(main())
