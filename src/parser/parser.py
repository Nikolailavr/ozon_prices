import asyncio
import json
import logging

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

from bot import send_msg
from core import settings
from core.database.schemas import LinkBase
from core.services import SubscribeService
from .checker import Checker

logger = logging.getLogger(__name__)


class Parser:
    def __init__(self):
        self.driver_options = uc.ChromeOptions()
        # self.driver_options.add_argument(
        #     "user-agent=Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0"
        # )
        # self.driver_options.add_argument("--no-sandbox")  # bypass OS security model
        # self.driver_options.add_argument(
        #     "--disable-blink-features=AutomationControlled"
        # )
        # self.driver_options.add_argument("--headless")
        # self.driver_options.add_argument(
        #     "--disable-dev-shm-usage"
        # )
        # self.driver_options.add_experimental_option(
        #     "excludeSwitches", ["enable-automation"]
        # )
        # self.driver_options.add_experimental_option("useAutomationExtension", False)

    async def start_checking(self) -> None:
        """Запуск проверки всех ссылок"""
        try:
            links = await SubscribeService.get_all(active=True)
            tasks = [self.check(link.url) for link in links]
            await asyncio.gather(*tasks)
        except Exception as ex:
            logger.error(ex)

    async def check(self, url: str) -> LinkBase | None:
        """Проверка одного продукта с использованием Chromium"""
        try:
            # Используем Chrome вместо Chrome, указывая options
            with uc.Chrome(
                options=self.driver_options,
                browser_executable_path="/usr/bin/chromium",  # Указываем путь к Chromium
            ) as driver:
                driver.implicitly_wait(5)
                driver.set_page_load_timeout(120)
                link = await self._get_link_data(driver, url)
                if link:
                    new_link = await Checker.check_price_changing(link)
                    if new_link:
                        subs = await SubscribeService.get_all(url=url)
                        for sub in subs:
                            await send_msg(
                                chat_id=sub.telegram_id,
                                text="Price is changed",
                            )
        except Exception as ex:
            logger.error(f"Error checking {url}: {ex}")
            # await self._notify_admin(f"[ERR] {link}: {ex}")

    async def _get_link_data(self, driver, url: str) -> LinkBase | None:
        """Получение данных о цене со страницы"""
        driver.get(url)
        await asyncio.sleep(2)
        title = self._clean_title(driver.title)
        attr = None
        try:
            price_element = driver.find_element(
                By.ID, value="state-webPrice-3121879-default-1"
            )
            attr = price_element.get_attribute("data-state")
        except Exception as ex:
            logger.error(f"Price parsing error: {ex}")
        if attr:
            return self.__unzip_price_data(
                attr=json.loads(attr),
                title=title,
                url=url,
            )

    @staticmethod
    def _clean_title(title: str) -> str:
        """Очистка заголовка от лишнего текста"""
        for text in settings.parser.text_for_replace_title:
            title = title.replace(text, "")
        return title.strip()

    @staticmethod
    def __unzip_price_data(attr: dict, title: str, url: str) -> LinkBase:
        ozon_price_data = attr.get("cardPrice", 0)
        price_data = attr.get("price", 0)
        logger.debug("Parsing is Ok")
        return LinkBase(
            url=url,
            title=title,
            ozon_price=ozon_price_data,
            price=price_data,
        )
