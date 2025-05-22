from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database.models import Base

if TYPE_CHECKING:
    from core.database.models import Subscribe


class Link(Base):
    url: Mapped[str] = mapped_column(
        Text, ForeignKey("subscribes.url"), primary_key=True, nullable=False
    )
    title: Mapped[str] = mapped_column(Text, nullable=True)
    ozon_price: Mapped[int] = mapped_column(Integer, default=0)
    price: Mapped[int] = mapped_column(Integer, default=0)
    old_price: Mapped[int] = mapped_column(Integer, default=0)

    subscribes: Mapped["Subscribe"] = relationship(back_populates="links")
