import html
from typing import Optional

from pydantic import BaseModel, field_validator, ConfigDict


class LinkBase(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    url: str
    title: str
    ozon_price: int  # Price with Ozon Card
    price: int  # Regular price

    @field_validator("ozon_price", "price", mode="before")
    @classmethod
    def clean_price(cls, value: str | int | None) -> Optional[int]:
        """Clean price string and convert to integer"""
        if value is None:
            return None
        if isinstance(value, int):
            return value
        try:
            cleaned_value = (
                value.replace("\u2009", "")  # Убираем тонкие пробелы
                .replace("₽", "")  # Убираем знак рубля
                .replace(" ", "")  # Убираем обычные пробелы
                .replace(" ", "")
                .strip()
            )
            return int(cleaned_value)
        except (AttributeError, ValueError) as e:
            raise ValueError(f"Некорректная цена: {value}")

    @field_validator("title", mode="before")
    @classmethod
    def decode_html_entities(cls, value: str) -> str:
        return html.unescape(value)


class LinkCreate(BaseModel):
    url: str


class LinkBig(LinkBase):
    ozon_price_old: int = 0
    price_old: int = 0
