import asyncio
import json
import logging

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from core import settings
from core.database.schemas.links import LinkBase

logger = logging.getLogger(__name__)


class Parser:
    def __init__(self):
        self.driver_options = uc.ChromeOptions()
        self.driver_options.add_argument(
            "user-agent=Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0"
        )
        self.driver_options.add_argument("--no-sandbox")  # bypass OS security model
        self.driver_options.add_argument(
            "--disable-blink-features=AutomationControlled"
        )
        self.driver_options.add_argument("--headless")
        self.driver_options.add_argument(
            "--disable-dev-shm-usage"
        )  # overcome limited resource problems
        self.driver_options.add_experimental_option(
            "excludeSwitches", ["enable-automation"]
        )
        self.driver_options.add_experimental_option("useAutomationExtension", False)

    async def start_checking(self) -> None:
        """Запуск проверки всех ссылок"""
        try:
            # links = await read_links()
            links = [
                "https://www.ozon.ru/product/solvie-proteinovoe-pechene-35-belka-kokos-sportivnoe-pechene-nizkokaloriynoe-bez-sahara-solvi-312031397/"
            ]
            tasks = [self.check(link) for link in links]
            await asyncio.gather(*tasks)
        except Exception as ex:
            logger.error(ex)

    async def check(self, link: str) -> LinkBase | None:
        """Проверка одного продукта с использованием Chromium"""
        try:
            # Используем Chrome вместо Chrome, указывая options
            with uc.Chrome(
                options=self.driver_options,
                browser_executable_path="/usr/bin/chromium",  # Указываем путь к Chromium
            ) as driver:
                driver.implicitly_wait(5)
                driver.set_page_load_timeout(120)
                price_data = await self._get_link_data(driver, link)
                logger.warning(self.__unzip_price_data(price_data))
        except Exception as ex:
            logger.error(f"Error checking {link}: {ex}")
            # await self._notify_admin(f"[ERR] {link}: {ex}")

    async def _get_link_data(self, driver, url: str) -> LinkBase | None:
        """Получение данных о цене со страницы"""
        driver.get(url)
        await asyncio.sleep(2)
        title = self._clean_title(driver.title)
        try:
            price_element = driver.find_element(
                By.ID, value="state-webPrice-3121879-default-1"
            )
            attr = price_element.get_attribute("data-state")
            return self.__unzip_price_data(
                attr=json.loads(attr),
                title=title,
                url=url,
            )
        except Exception as ex:
            logger.error(f"Price parsing error: {ex}")

    @staticmethod
    def _clean_title(title: str) -> str:
        """Очистка заголовка от лишнего текста"""
        for text in settings.parser.text_for_replace_title:
            title = title.replace(text, "")
        return title.strip()

    @staticmethod
    def __unzip_price_data(attr: dict, title: str, url: str) -> LinkBase:
        ozon_price_data = attr.get("state").get("cardPrice", "0")
        price_data = attr.get("state").get("price", "0")
        return LinkBase(
            url=url,
            title=title,
            ozon_price=ozon_price_data,
            price=price_data,
        )


parser = Parser()


async def main():
    await parser.start_checking()


if __name__ == "__main__":
    asyncio.run(main())
