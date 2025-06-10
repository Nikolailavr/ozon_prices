from sqlalchemy import BigInteger, String, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column

from core.database.models.base import Base


class User(Base):
    telegram_id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, nullable=False
    )
    url: Mapped[str] = mapped_column(Text, nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=False)
    last_command: Mapped[str] = mapped_column(String(30), default="")
