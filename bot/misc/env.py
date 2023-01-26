from os import environ
from typing import Final


class TgKeys:
    TOKEN: Final = environ.get('OzonToken', 'define me!')
    admin_chatID = 161622650
