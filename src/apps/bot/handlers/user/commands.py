import logging
from aiogram import Router, F, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from aiogram.filters import Command

from core import settings
from core.services import UserService

logger = logging.getLogger(__name__)
router = Router()


class UserStates(StatesGroup):
    waiting_url = State()


@router.message(Command("start"))
async def __start(msg: Message) -> None:
    text = f"Привет, <b>{msg.from_user.first_name}</b>!\n{settings.msg.HELP_MESSAGE}"
    await msg.answer(text)
    await UserService.get_or_create_user(telegram_id=msg.from_user.id)


@router.message(Command("help"))
async def __help(msg: Message) -> None:
    await msg.answer(settings.msg.HELP_MESSAGE)


@router.message(Command("add"))
async def __add(msg: Message, state: FSMContext) -> None:
    await state.set_state(UserStates.waiting_url)
    await msg.answer(settings.msg.MSG_ADD)


@router.message(UserStates.waiting_url)
async def __add_url(message: Message, state: FSMContext):
    if message.text.startswith("https://www.ozon.ru/"):
        url = message.text.rstrip("/")  # Удаляем trailing slash
        try:
            await UserService.update(telegram_id=message.from_user.id, url=url)
            await message.answer(settings.msg.GOOD_URL)
        except Exception as ex:
            logger.error(f"Error adding link: {ex}")
            await message.answer(settings.msg.BAD_URL)
    else:
        await message.answer(settings.msg.BAD_URL)
    await state.clear()


@router.message(Command("delete"))
async def __delete(msg: Message) -> None:
    await msg.answer(settings.msg.MSG_DELETE)
    await UserService.update(
        telegram_id=msg.from_user.id,
        command="/delete",
    )


def register_users_handlers(dp: Dispatcher) -> None:
    dp.include_router(router)
