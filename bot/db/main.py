from dataclasses import dataclass


@dataclass
class User:
    id: int
    command: str


@dataclass
class Link:
    id: int
    url: str
    price: int
    price_ozon: int

    def __init__(self,
                 id: int,
                 url: str,
                 price: int = 0,
                 price_ozon: int = 0):
        self.id = id
        self.url = url
        self.price = price
        self.price_ozon = price_ozon



