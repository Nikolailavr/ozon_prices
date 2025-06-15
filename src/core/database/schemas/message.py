from pydantic import BaseModel


class TelegramMessage(BaseModel):
    chat_id: int
    text: str
