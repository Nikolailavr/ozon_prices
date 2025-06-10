from pydantic import BaseModel


class UserBase(BaseModel):
    telegram_id: int


class UserRead(UserBase):
    url: str = None
    active: bool = False
    last_command: str = ""
