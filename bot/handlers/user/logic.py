from aiogram import Bot
from aiogram.types import Message
from bot.db import add_link, read_links, delete_link, update_last_command
from bot.db.main import User
from bot.misc import MSG_ADD, MSG_DELETE, logger


async def _add(msg: Message) -> None:
    bot: Bot = msg.bot
    await bot.send_message(chat_id=msg.from_user.id, text=MSG_ADD)
    await update_last_command(User(id=msg.from_user.id, command="/add"))


async def _delete(msg: Message) -> None:
    bot: Bot = msg.bot
    await bot.send_message(chat_id=msg.from_user.id, text=MSG_DELETE)
    await update_last_command(User(id=msg.from_user.id, command="/delete"))


async def _list(msg: Message) -> None:
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
