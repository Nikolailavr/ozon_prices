from sqlalchemy import ForeignKey, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database.models.base import Base


class Link(Base):
    url: Mapped[str] = mapped_column(
        Text, ForeignKey("links.url"), primary_key=True, nullable=False
    )
    title: Mapped[str] = mapped_column(Text, nullable=True)
    ozon_price: Mapped[int] = mapped_column(Integer, default=0)
    price: Mapped[int] = mapped_column(Integer, default=0)
    old_price: Mapped[int] = mapped_column(Integer, default=0)

    link: Mapped["Link"] = relationship(back_populates="price")
