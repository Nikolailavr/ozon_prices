from pydantic import BaseModel


class UserBase(BaseModel):
    telegram_id: int
