import logging
from aiogram import Router, F, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from src.bot.db import read_links, update_last_command
from src.bot.db.main import User
from src.bot.misc import config, TgKeys
import requests

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("start"))
async def __start(msg: Message) -> None:
    text = f"Привет, <b>{msg.from_user.first_name}</b>!\n{config.HELP_MESSAGE}"
    await msg.answer(text)
    await update_last_command(User(id=msg.from_user.id, command=""))


@router.message(Command("help"))
async def __help(msg: Message) -> None:
    await msg.answer(config.HELP_MESSAGE)
    await update_last_command(User(id=msg.from_user.id, command=""))


@router.message(Command("add"))
async def __add(msg: Message) -> None:
    with open(config.example_url, "rb") as photo:
        await msg.answer_photo(photo=photo, caption=config.CAPTION_EX_URL)
    await msg.answer(config.MSG_ADD)
    await update_last_command(User(id=msg.from_user.id, command="/add"))


@router.message(Command("delete"))
async def __delete(msg: Message) -> None:
    await msg.answer(config.MSG_DELETE)
    await update_last_command(User(id=msg.from_user.id, command="/delete"))


@router.message(Command("list"))
async def __list(msg: Message) -> None:
    await update_last_command(User(id=msg.from_user.id, command=""))
    result = "Список url из вашей подписки:\n\n"
    try:
        links = await read_links(telegram_id=msg.from_user.id)
    except Exception as ex:
        logger.error(ex)
    else:
        for index, link in enumerate(links, 1):
            result += f"{index}. {link.url}\n"
        await msg.answer(result)


@router.message(Command("myip"))
async def __myip(msg: Message) -> None:
    if str(msg.from_user.id) == TgKeys.admin_chatID:
        url = "https://ipwho.is/"
        text = "IP адрес не найден"
        response = requests.get(url=url)
        if response.status_code == 200:
            text = response.json().get("ip")
        await msg.answer(text)


def register_users_handlers(dp: Dispatcher) -> None:
    dp.include_router(router)
