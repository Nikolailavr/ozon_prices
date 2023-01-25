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
