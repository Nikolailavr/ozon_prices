from aiogram import Dispatcher, Bot
from aiogram.types import Message, CallbackQuery, PreCheckoutQuery, ContentType
from aiogram.dispatcher import FSMContext

from bot.misc import HELP_MESSAGE
from bot.handlers.user.logic import _add, _list, _delete


async def __start(msg: Message) -> None:
    bot: Bot = msg.bot
    text = f"Привет, <b>{msg.from_user.first_name}</b>!\n{HELP_MESSAGE}"
    await bot.send_message(chat_id=msg.from_user.id, text=text)



async def __help(msg: Message) -> None:
    bot: Bot = msg.bot
    await bot.send_message(chat_id=msg.from_user.id, text=HELP_MESSAGE)


async def __add(msg: Message) -> None:
    await _add(msg=msg)


async def __delete(msg: Message) -> None:
    await _delete(msg=msg)


async def __list(msg: Message) -> None:
    await _list(msg=msg)


def register_users_handlers(dp: Dispatcher) -> None:
    # region Msg handlers
    dp.register_message_handler(__start, commands=["start"])
    dp.register_message_handler(__add, commands=["add"])
    dp.register_message_handler(__delete, commands=["delete"])
    dp.register_message_handler(__list, commands=["list"])
    dp.register_message_handler(__help, commands=["help"])

    # region Callback handlers

    # region other handlers
