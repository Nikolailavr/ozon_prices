from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, Text, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database.models.base import Base

if TYPE_CHECKING:
    from core.database.models.users import User


class Subscribe(Base):
    telegram_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.telegram_id"), nullable=False
    )
    url: Mapped[str] = mapped_column(Text, primary_key=True, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped["User"] = relationship(back_populates="subscribe")
    price: Mapped["Link"] = relationship(back_populates="link")


class Link(Base):
    url: Mapped[str] = mapped_column(
        Text, ForeignKey("links.url"), primary_key=True, nullable=False
    )
    title: Mapped[str] = mapped_column(Text, nullable=True)
    ozon_price: Mapped[int] = mapped_column(Integer, default=0)
    price: Mapped[int] = mapped_column(Integer, default=0)
    old_price: Mapped[int] = mapped_column(Integer, default=0)

    link: Mapped["Link"] = relationship(back_populates="price")
