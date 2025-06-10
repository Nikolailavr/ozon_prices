from typing import Optional

from pydantic import BaseModel


class UserBase(BaseModel):
    telegram_id: int


class UserRead(UserBase):
    url: Optional[str] = None
    active: bool = False
    last_command: Optional[str] = ""
