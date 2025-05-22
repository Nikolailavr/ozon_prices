from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database.models.base import Base

if TYPE_CHECKING:
    from core.database.models import User, Link


class Subscribe(Base):
    telegram_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.telegram_id"), nullable=False
    )
    url: Mapped[str] = mapped_column(Text, primary_key=True, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=False)

    users: Mapped["User"] = relationship(back_populates="subscribes")
    links: Mapped["Link"] = relationship(back_populates="subscribes")
