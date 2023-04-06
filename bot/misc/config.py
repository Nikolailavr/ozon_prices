import os

from selenium import webdriver

# Paths
driver_path = "./home/lnv/soft/ozon_prices/chrome/chromedriver"
example_url = "/home/lnv/soft/ozon_prices/bot/misc/example_url.png"
SQLITE_DB_FILE = "db.sqlite3"

# ChromeOptions
options = webdriver.ChromeOptions()
options.add_argument("user-agent=Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0")
options.add_argument("--no-sandbox")  # bypass OS security model
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--headless")
options.add_argument("--disable-dev-shm-usage")  # overcome limited resource problems
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
proxy = os.getenv('proxy')
#options.add_argument(f"--proxy-server={proxy}")

# Others
text_for_replace_title = " - купить по выгодным ценам в интернет-магазине OZON"

# Messages
HELP_MESSAGE = """
Доступные команды бота:
/help - показать список доступных команд
/add - добавить новый url для подписки
/list - показать список url в подписке
/delete - удалить url из подписки"""

MSG_ADD = """Чтобы добавить новый url в подписку отправьте его в сообщении"""

MSG_DELETE = """Чтобы удалить url из подписки отправьте его в сообщении"""

BAD_MSG = "Я вас не понял, чтобы кзнать доступные команды наберите /help"

BAD_URL = """Ваш url имеет неверный формат, пожалуйста, убедитесь что вы правильно скопировали ссылку на товар.
Ваша ссылка должна начинаться с https://www.ozon.ru/product/"""

GOOD_URL = """Ваш url успешно добавлен в подписку!"""

GOOD_DELETE = """Ваш url успешно удален из подписки!"""

CAPTION_EX_URL = """Пример как правильно скопировать url (выделено синим цветом)"""
