from core.database.schemas import (
    LinkBase,
    UserRead,
)

import re


def price_change(user: UserRead, link: LinkBase):
    # Экранируем только текст без ссылки
    text_escaped = escape_markdown(
        f"🔔 Обновление цены!\n"
        f"📦 {link.title}\n"
        f"💰 Новая цена: {link.ozon_price} ₽\n"
    )
    # Добавляем ссылку отдельно, без экранирования
    text = f"{text_escaped}🔗 [Посмотреть товар]({link.url})"
    return {
        "chat_id": user.telegram_id,
        "text": text,
    }


def escape_markdown(text: str) -> str:
    escape_chars = r"\_*[]()~`>#+-=|{}.!"
    return re.sub(f"([{re.escape(escape_chars)}])", r"\\\1", text)
