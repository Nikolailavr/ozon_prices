from aiogram import Dispatcher

from src.bot.handlers.other import register_other_handlers
from src.bot.handlers.user import register_users_handlers


def register_all_handlers(dp: Dispatcher) -> None:
    handlers = (
        register_users_handlers,
        register_other_handlers,
    )
    for handler in handlers:
        handler(dp)
