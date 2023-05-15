from aiogram import Dispatcher, Bot
from aiogram.types import Message

from bot.db import read_user, add_link, delete_link, update_last_command, update_price
from bot.db.main import User, Link
from bot.misc import logger, config


async def other_messages(msg: Message) -> None:
    user: User = await read_user(telegram_id=msg.from_user.id)
    match user.command:
        case "/add":
            await __add_link(msg=msg)
            await update_last_command(data=User(id=msg.from_user.id, command=""))
        case "/delete":
            await __delete_link(msg=msg)
            await update_last_command(data=User(id=msg.from_user.id, command=""))
        case _:
            bot: Bot = msg.bot
            await bot.send_message(msg.from_user.id, config.BAD_MSG)
            await update_last_command(data=User(id=msg.from_user.id, command=""))


async def __add_link(msg: Message) -> None:
    if msg.text.startswith("https://www.ozon.ru/product/"):
        url = msg.text
        if url[-1] == "/":
            url = url[:-1]
        try:
            await add_link(link=Link(id=msg.from_user.id, url=url))
            await update_price(link=Link(id=msg.from_user.id, url=url))
        except Exception as ex:
            logger.error(ex)
        else:
            bot: Bot = msg.bot
            await bot.delete_message(chat_id=msg.from_user.id, message_id=msg.message_id)
            await bot.send_message(chat_id=msg.from_user.id, text=config.GOOD_URL)
    else:
        bot: Bot = msg.bot
        await bot.send_message(chat_id=msg.from_user.id, text=config.BAD_URL)


async def __delete_link(msg: Message) -> None:
    try:
        await delete_link(link=Link(id=msg.from_user.id, url=msg.text))
    except Exception as ex:
        logger.error(ex)
    else:
        bot: Bot = msg.bot
        await bot.delete_message(chat_id=msg.from_user.id, message_id=msg.message_id)
        await bot.send_message(chat_id=msg.from_user.id, text=config.GOOD_DELETE)


def register_other_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(other_messages, content_types=['text'], state=None)
