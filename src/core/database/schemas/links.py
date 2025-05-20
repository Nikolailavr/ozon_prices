from typing import Optional

from pydantic import BaseModel, field_validator, ConfigDict


class LinkBase(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )  # If you need to handle non-standard types

    url: str
    title: str
    ozon_price: int  # Price with Ozon Card
    price: int  # Regular price
    old_price: Optional[int] = None  # Original strikethrough price

    @field_validator("ozon_price", "price", "old_price", mode="before")
    @classmethod
    def clean_price(cls, value: str | int | None) -> Optional[int]:
        """Clean price string and convert to integer"""
        if value is None:
            return None
        if isinstance(value, int):
            return value
        try:
            return int(value.replace(" ", "").replace("₽", "").strip())
        except (AttributeError, ValueError) as e:
            raise ValueError(f"Invalid price format: {value}") from e
