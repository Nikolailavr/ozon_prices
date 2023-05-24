import os
from typing import Final
from dotenv import load_dotenv


load_dotenv()


class TgKeys:
    TOKEN: Final = os.getenv('OzonToken', 'define me!')
    admin_chatID = os.getenv('AdminID', 'define me!')

