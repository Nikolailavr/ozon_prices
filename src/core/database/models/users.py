from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database.models.base import Base

if TYPE_CHECKING:
    from core.database.models import Subscribe


class User(Base):
    telegram_id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, nullable=False
    )
    last_command: Mapped[str] = mapped_column(String(30), default="")

    subscribes: Mapped[list["Subscribe"]] = relationship(back_populates="users")
