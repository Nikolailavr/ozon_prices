import logging

import requests
from aiogram import Router, F, Dispatcher
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message

from apps.celery.parser import parser_login, parser_check, parser_check_all
from core import settings, async_redis_client
from core.services.users.user_service import UserService

logger = logging.getLogger(__name__)
router = Router()


class LoginStates(StatesGroup):
    waiting_code = State()


@router.message(Command("login"))
async def cmd_login(message: Message, state: FSMContext):
    if message.chat.id != settings.telegram.admin_chat_id:
        return  # игнорим остальных

    await message.answer(
        "Запуск процесс авторизации. Отправьте код подтверждения, когда он придет."
    )
    await state.set_state(LoginStates.waiting_code)

    # Запускаем парсер (асинхронно или в фоне)
    logger.info("Запускаем парсер")
    parser_login.delay()


@router.message(LoginStates.waiting_code, F.chat.id == settings.telegram.admin_chat_id)
async def process_code(message: Message, state: FSMContext):
    code = message.text.strip()
    if not code.isdigit() or len(code) != 6:
        await message.answer("Пожалуйста, введите 6-значный числовой код.")
        return

    await async_redis_client.set("login_otp_code", code, ex=300)  # код живет 5 минут
    await message.answer("Код получен")
    await state.clear()


@router.message(Command("check"))
async def cmd_check(message: Message):
    if message.chat.id != settings.telegram.admin_chat_id:
        return  # игнорим остальных
    logger.info("Запускаем проверку")
    user = await UserService.get_or_create_user(message.from_user.id)
    if user.url:
        parser_check.delay(user.telegram_id)
        await message.answer("Запускаем проверку")
    else:
        await message.answer("У вас нет активной подписки")


@router.message(Command("check_all"))
async def cmd_check_all(message: Message):
    if message.chat.id != settings.telegram.admin_chat_id:
        return  # игнорим остальных
    logger.info("Запускаем проверку всех пользователей")
    parser_check_all.delay()
    await message.answer("Запускаем проверку всех пользователей")


@router.message(Command("del_cookie"))
async def cmd_delete_cookie(message: Message):
    if message.chat.id != settings.telegram.admin_chat_id:
        return  # игнорим остальных
    await async_redis_client.delete("cookies")
    await message.answer("Cookie удалены")


@router.message(Command("myip"))
async def __myip(msg: Message) -> None:
    if str(msg.from_user.id) == settings.telegram.admin_chat_id:
        url = "https://ipwho.is/"
        text = "IP адрес не найден"
        response = requests.get(url=url)
        if response.status_code == 200:
            text = response.json().get("ip")
        await msg.answer(text)


def register_admin_handlers(dp: Dispatcher) -> None:
    dp.include_router(router)
