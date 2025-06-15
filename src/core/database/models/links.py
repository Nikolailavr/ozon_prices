from sqlalchemy import Text, Integer
from sqlalchemy.orm import Mapped, mapped_column

from core.database.models import Base


class Link(Base):
    url: Mapped[str] = mapped_column(Text, primary_key=True, nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=True)
    ozon_price: Mapped[int] = mapped_column(Integer, default=0)
    price: Mapped[int] = mapped_column(Integer, default=0)
