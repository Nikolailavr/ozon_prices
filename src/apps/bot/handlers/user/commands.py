import logging
from aiogram import Router, F, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command

from core import settings
from core.services import UserService

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("start"))
async def __start(msg: Message) -> None:
    text = f"Привет, <b>{msg.from_user.first_name}</b>!\n{settings.msg.HELP_MESSAGE}"
    await msg.answer(text)
    await UserService.get_or_create_user(telegram_id=msg.from_user.id)


@router.message(Command("help"))
async def __help(msg: Message) -> None:
    await msg.answer(settings.msg.HELP_MESSAGE)


@router.message(Command("add"))
async def __add(msg: Message) -> None:
    await msg.answer(settings.msg.MSG_ADD)
    await UserService.update(
        telegram_id=msg.from_user.id,
        command="/add",
    )


@router.message(Command("delete"))
async def __delete(msg: Message) -> None:
    await msg.answer(settings.msg.MSG_DELETE)
    await UserService.update(
        telegram_id=msg.from_user.id,
        command="/delete",
    )


# @router.message(Command("list"))
# async def __list(msg: Message) -> None:
#     result = "Список url из вашей подписки:\n\n"
#     try:
#         subs = await SubscribeService.get_all(telegram_id=msg.from_user.id)
#     except Exception as ex:
#         logger.error(ex)
#     else:
#         for index, item in enumerate(subs, 1):
#             result += f"{index}. {item.url}\n"
#         await msg.answer(result)


def register_users_handlers(dp: Dispatcher) -> None:
    dp.include_router(router)
