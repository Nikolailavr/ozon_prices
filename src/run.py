import asyncio
import logging
import threading

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from apps.bot import start_bot
from apps.parser import Parser
from core import settings

parser = Parser()

logger = logging.getLogger(__name__)


def run_scheduler():
    """Запуск планировщика в отдельном потоке"""

    logger.info("Запуск планировщика в отдельном потоке")
    # Создаем новый event loop для этого потока
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    scheduler = AsyncIOScheduler(event_loop=loop)
    scheduler.add_job(
        parser.start_checking,
        "interval",
        hours=settings.schedule.interval,
    )
    try:
        scheduler.start()
        loop.run_forever()
    finally:
        scheduler.shutdown()
        loop.close()


def main():
    # Создаем и запускаем поток для планировщика
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()

    # Запускаем бота в основном потоке
    logger.info("Запускаем бота в основном потоке")
    asyncio.run(start_bot())


if __name__ == "__main__":
    main()
