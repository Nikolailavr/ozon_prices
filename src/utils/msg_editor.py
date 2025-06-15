from core.database.schemas import (
    LinkBase,
    TelegramMessage,
    UserRead,
)


def price_change(user: UserRead, link: LinkBase):
    text = (
        f"🔔 Обновление цены!\n "
        f"📦 {link.title}\n"
        f"💰 Новая цена: {link.ozon_price} ₽\n"
        f"🔗 [Посмотреть товар]({link.url})"
    )
    return {
        "chat_id": user.telegram_id,
        "text": text,
    }
