import logging
from aiogram import Router, Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import StateFilter

from core import settings
from core.services import UserService


logger = logging.getLogger(__name__)
router = Router()


@router.message(StateFilter(None))
async def other_messages(msg: Message, bot: Bot) -> None:
    """
    Обработка всех текстовых сообщений
    """
    user = await UserService.get_or_create_user(telegram_id=msg.from_user.id)
    match user.last_command:
        case "/add":
            await handle_add_link(msg, bot)
            await UserService.update(
                telegram_id=msg.from_user.id,
                command="",
            )
        case "/delete":
            await handle_delete_link(msg, bot)
            await UserService.update(
                telegram_id=msg.from_user.id,
                command="",
            )
        case _:
            await msg.answer(settings.msg.BAD_MSG)
            await UserService.update(
                telegram_id=msg.from_user.id,
                command="",
            )


async def handle_add_link(msg: Message, bot: Bot) -> None:
    """
    Обработка добавления ссылки
    """
    if msg.text.startswith("https://www.ozon.ru/"):
        url = msg.text.rstrip("/")  # Удаляем trailing slash
        try:
            await UserService.update(telegram_id=msg.from_user.id, url=url)
            await bot.delete_message(
                chat_id=msg.from_user.id, message_id=msg.message_id
            )
            await msg.answer(settings.msg.GOOD_URL)
        except Exception as ex:
            logger.error(f"Error adding link: {ex}")
            await msg.answer(settings.msg.BAD_URL)
    else:
        await msg.answer(settings.msg.BAD_URL)


async def handle_delete_link(msg: Message, bot: Bot) -> None:
    """
    Обработка удаления ссылки
    """
    try:
        await UserService.update(
            telegram_id=msg.from_user.id,
            url="",
        )
        await bot.delete_message(chat_id=msg.from_user.id, message_id=msg.message_id)
        await msg.answer(settings.msg.GOOD_DELETE)
    except Exception as ex:
        logger.error(f"Error deleting link: {ex}")
        await msg.answer("Произошла ошибка при удалении ссылки")


def register_other_handlers(dp: Dispatcher) -> None:
    """Регистрация обработчиков"""
    dp.include_router(router)
