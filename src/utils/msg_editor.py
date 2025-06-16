from core import settings
from core.database.schemas import (
    LinkBig,
    UserRead,
)

import re


def check_price(link: LinkBig):
    if link.ozon_price < link.ozon_price_old:
        return f"🟢⬇️ *Цена снижена!*\n"
    else:
        return f"🔴⬆️ *Цена увеличилась!*\n"


def price_change(user: UserRead, link: LinkBig):
    title = check_price(link)
    # Экранируем только текст без ссылки
    text_escaped = escape_markdown(f"📦 {link.title}\n")
    price_text = (
        f"💰 *Старая цена:* {link.ozon_price_old} ₽\n"
        f"💰 *Новая цена:* {link.ozon_price} ₽\n"
    )
    # Добавляем ссылку отдельно, без экранирования
    text = f"{title}{text_escaped}{price_text}🔗 [Посмотреть товар]({link.url})"
    return {
        "chat_id": user.telegram_id,
        "text": text,
    }


def escape_markdown(text: str) -> str:
    escape_chars = r"\_*[]()~`>#+-=|{}.!"
    return re.sub(f"([{re.escape(escape_chars)}])", r"\\\1", text)


def need_authorization():
    return {
        "chat_id": settings.telegram.admin_chat_id,
        "text": "Требуется авторизация, куки устарели или недоступны",
    }
