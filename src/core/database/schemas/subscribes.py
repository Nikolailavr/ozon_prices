from pydantic import BaseModel


class SubscribeBase(BaseModel):
    telegram_id: int
    url: str
