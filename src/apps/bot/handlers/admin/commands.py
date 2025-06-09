import logging
from aiogram import Router, F, Dispatcher
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message

from apps.celery.tasks import parser_login
from core import settings, async_redis_client

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


def register_admin_handlers(dp: Dispatcher) -> None:
    dp.include_router(router)
