from aiogram import Dispatcher
from aiogram import Bot
from aiogram.types import Message

from bot.db import read_links, update_last_command
from bot.db.main import User
from bot.misc import config, logger, TgKeys
import requests


async def __start(msg: Message) -> None:
    bot: Bot = msg.bot
    text = f"Привет, <b>{msg.from_user.first_name}</b>!\n{config.HELP_MESSAGE}"
    await bot.send_message(chat_id=msg.from_user.id, text=text)
    await update_last_command(User(id=msg.from_user.id, command=""))


async def __help(msg: Message) -> None:
    bot: Bot = msg.bot
    await bot.send_message(chat_id=msg.from_user.id, text=config.HELP_MESSAGE)
    await update_last_command(User(id=msg.from_user.id, command=""))


async def __add(msg: Message) -> None:
    bot: Bot = msg.bot
    with open(config.example_url, "rb") as photo:
        await bot.send_photo(chat_id=msg.from_user.id, photo=photo, caption=config.CAPTION_EX_URL)
    await bot.send_message(chat_id=msg.from_user.id, text=config.MSG_ADD)
    await update_last_command(User(id=msg.from_user.id, command="/add"))


async def __delete(msg: Message) -> None:
    bot: Bot = msg.bot
    await bot.send_message(chat_id=msg.from_user.id, text=config.MSG_DELETE)
    await update_last_command(User(id=msg.from_user.id, command="/delete"))


async def __list(msg: Message) -> None:
    await update_last_command(User(id=msg.from_user.id, command=""))
    result = "Список url из вашей подписки:\n\n"
    try:
        links = await read_links(telegram_id=msg.from_user.id)
    except Exception as ex:
        logger.error(ex)
    else:
        bot: Bot = msg.bot
        for index, link in enumerate(links, 1):
            result += f"{index}. {link.url}\n"
        await bot.send_message(chat_id=msg.from_user.id, text=result)


async def __myip(msg: Message) -> None:
    if str(msg.from_user.id) == TgKeys.admin_chatID:
        url = "https://ipwho.is/"
        text = "IP адрес не найден"
        response = requests.get(url=url)
        if response.status_code == 200:
            text = response.json().get('ip')
        bot: Bot = msg.bot
        await bot.send_message(chat_id=msg.from_user.id, text=text)


def register_users_handlers(dp: Dispatcher) -> None:
    # region Msg handlers
    dp.register_message_handler(__start, commands=["start"])
    dp.register_message_handler(__add, commands=["add"])
    dp.register_message_handler(__delete, commands=["delete"])
    dp.register_message_handler(__list, commands=["list"])
    dp.register_message_handler(__help, commands=["help"])
    dp.register_message_handler(__myip, commands=["myip"])

    # region Callback handlers

    # region other handlers
