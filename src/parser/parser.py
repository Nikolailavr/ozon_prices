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
        self.driver = None
        self.options = uc.ChromeOptions()
        # Основные настройки
        self.options.add_argument("--disable-blink-features=AutomationControlled")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")

        # Настройки для маскировки
        self.options.add_argument("--disable-infobars")
        self.options.add_argument("--disable-extensions")

        # Обязательные параметры для headless
        # self.options.add_argument("--headless=new")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument("--disable-gpu")

        # Разрешение экрана (важно для корректного рендеринга)
        self.options.add_argument("--window-size=1920,1080")

        # Параметры для экономии ресурсов
        self.options.add_argument("--disable-software-rasterizer")
        self.options.add_argument("--disable-setuid-sandbox")

        # Отключение кэша (опционально)
        self.options.add_argument("--disk-cache-size=0")
        self.options.add_argument("--media-cache-size=0")

        # Реалистичный user-agent
        self.options.add_argument(
            "user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

    async def start_checking(self) -> None:
        """Запуск проверки всех ссылок"""
        try:
            links = await SubscribeService.get_all(active=True)
            self._driver_run()
            for link in links:
                await self.check(link.url)
            self.driver.quit()
        except Exception as ex:
            logger.error(ex)

    async def check(self, url: str):
        need_quit = False
        if self.driver is None:
            self._driver_run()
            need_quit = True
        logger.info(f"Start checking {url}")
        link = await self._get_url_data(url)
        if link:
            new_link = await Checker.check_price_changing(link)
            if new_link:
                subs = await SubscribeService.get_all(url=url)
                for sub in subs:
                    await send_msg(
                        chat_id=sub.telegram_id,
                        text="Price is changed",
                    )
        if need_quit:
            self.driver.quit()

    def _driver_run(self):
        try:
            self.driver = uc.Chrome(
                driver_executable_path=settings.parser.driver_path,
                options=self.options,
                browser_executable_path="/usr/bin/chromium",
                use_subprocess=False,
            )
            self.driver.implicitly_wait(5)
            self.driver.set_page_load_timeout(120)
        except Exception as ex:
            logger.error("Error in run driver")

    async def _get_url_data(self, url: str) -> LinkBase | None:
        try:
            self.driver.get(url)
            await asyncio.sleep(1)
            title = self._clean_title(self.driver.title)
            price_element = self.driver.find_element(
                By.ID, value="state-webPrice-3121879-default-1"
            )
            attr = price_element.get_attribute("data-state")
            logger.info(f"{attr=}")
            return self.__unzip_price_data(
                attr=json.loads(attr),
                title=title,
                url=url,
            )
        except Exception as ex:
            logger.error(f"Error get data from url ({url}): {ex}")
            await send_msg(
                chat_id=settings.telegram.admin_chat_id,
                text=f"Error get data from url {url}: {ex}",
            )
            return None

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
        logger.info("Unzip price data is OK")
        return LinkBase(
            url=url,
            title=title,
            ozon_price=ozon_price_data,
            price=price_data,
        )
