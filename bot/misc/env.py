import os
from typing import Final


class TgKeys:
    TOKEN: Final = os.getenv('OzonToken', 'define me!')
    admin_chatID = os.getenv('AdminID', 'define me!')
