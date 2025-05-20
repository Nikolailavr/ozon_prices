import logging
from aiogram import Router, Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import StateFilter
from src.bot.db import (
    read_user,
    add_link,
    delete_link,
    update_last_command,
    update_price,
)
from src.bot.db.main import User, Link
from src.bot.misc import config

logger = logging.getLogger(__name__)
router = Router()


@router.message(StateFilter(None))
async def other_messages(msg: Message, bot: Bot) -> None:
    """Обработка всех текстовых сообщений"""
    user = await read_user(telegram_id=msg.from_user.id)

    match user.command:
        case "/add":
            await handle_add_link(msg, bot)
            await update_last_command(data=User(id=msg.from_user.id, command=""))
        case "/delete":
            await handle_delete_link(msg, bot)
            await update_last_command(data=User(id=msg.from_user.id, command=""))
        case _:
            await msg.answer(config.BAD_MSG)
            await update_last_command(data=User(id=msg.from_user.id, command=""))


async def handle_add_link(msg: Message, bot: Bot) -> None:
    """Обработка добавления ссылки"""
    if msg.text.startswith("https://www.ozon.ru/product/"):
        url = msg.text.rstrip("/")  # Удаляем trailing slash

        try:
            await add_link(link=Link(id=msg.from_user.id, url=url))
            await update_price(link=Link(id=msg.from_user.id, url=url))
            await bot.delete_message(
                chat_id=msg.from_user.id, message_id=msg.message_id
            )
            await msg.answer(config.GOOD_URL)
        except Exception as ex:
            logger.error(f"Error adding link: {ex}")
            await msg.answer(config.BAD_URL)
    else:
        await msg.answer(config.BAD_URL)


async def handle_delete_link(msg: Message, bot: Bot) -> None:
    """Обработка удаления ссылки"""
    try:
        await delete_link(link=Link(id=msg.from_user.id, url=msg.text))
        await bot.delete_message(chat_id=msg.from_user.id, message_id=msg.message_id)
        await msg.answer(config.GOOD_DELETE)
    except Exception as ex:
        logger.error(f"Error deleting link: {ex}")
        await msg.answer("Произошла ошибка при удалении ссылки")


def register_other_handlers(dp: Dispatcher) -> None:
    """Регистрация обработчиков"""
    dp.include_router(router)
