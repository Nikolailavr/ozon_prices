from core import settings
from core.database.schemas import (
    LinkBig,
    UserRead,
)

import re


def check_price(link: LinkBig):
    if link.ozon_price < link.ozon_price_old:
        if link.ozon_price == 0:
            return out_of_stock_message(link)
        elif link.ozon_price_old == 0:
            return in_stock_message(link)
        else:
            return lower_price(link)
    else:
        return high_price(link)


def lower_price(link: LinkBig):
    return (
        f"🟢⬇️ *Цена снижена!*\n"
        f"📦 {escape_markdown(link.title)}\n"
        f"💰 *Старая цена:* {link.ozon_price_old} ₽\n"
        f"💰 *Новая цена:* {link.ozon_price} ₽\n"
        f"🔗 [Посмотреть товар]({link.url})"
    )


def high_price(link: LinkBig):
    return (
        f"🔴⬆️ *Цена увеличилась!*\n"
        f"📦 {escape_markdown(link.title)}\n"
        f"💰 *Старая цена:* {link.ozon_price_old} ₽\n"
        f"💰 *Новая цена:* {link.ozon_price} ₽\n"
        f"🔗 [Посмотреть товар]({link.url})"
    )


def price_change(user: UserRead, link: LinkBig):
    return {
        "chat_id": user.telegram_id,
        "text": check_price(link),
    }


def escape_markdown(text: str) -> str:
    escape_chars = r"\_*[]()~`>#+-=|{}.!"
    return re.sub(f"([{re.escape(escape_chars)}])", r"\\\1", text)


def need_authorization():
    return {
        "chat_id": settings.telegram.admin_chat_id,
        "text": "Требуется авторизация, куки устарели или недоступны",
    }


def out_of_stock_message(link: LinkBig):
    return (
        f"🔴 *Товар недоступен!*\n"
        f"📦 {escape_markdown(link.title)}\n"
        f"❌ Сейчас товар отсутствует в наличии.\n"
        f"🔗 [Посмотреть товар]({link.url})"
    )


def in_stock_message(link: LinkBig):
    return (
        f"🟢 *Товар в наличии!*\n"
        f"📦 {escape_markdown(link.title)}\n"
        f"💰 *Цена:* {link.ozon_price} ₽\n"
        f"🔗 [Посмотреть товар]({link.url})"
    )
