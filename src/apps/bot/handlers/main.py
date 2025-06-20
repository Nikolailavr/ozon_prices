from aiogram import Dispatcher

from apps.bot.handlers.other import register_other_handlers
from apps.bot.handlers.user import register_users_handlers
from apps.bot.handlers.admin import register_admin_handlers


def register_all_handlers(dp: Dispatcher) -> None:
    handlers = (
        register_admin_handlers,
        register_users_handlers,
        register_other_handlers,
    )
    for handler in handlers:
        handler(dp)
