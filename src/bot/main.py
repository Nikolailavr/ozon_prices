import asyncio
import json
import logging

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from aiogram import Bot
from core import settings

logger = logging.getLogger(__name__)


class Monitoring:
    def __init__(self):
        self.bot = Bot(token=settings.telegram.token, parse_mode="HTML")
        self.driver_options = uc.ChromeOptions()
        self._configure_driver_options()

    def _configure_driver_options(self):
        """Настройка опций для драйвера с использованием Chromium"""
        # Указываем путь к исполняемому файлу Chromium
        self.driver_options.binary_location = "/usr/bin/chromium"

        self.driver_options.add_argument("--headless=new")
        self.driver_options.add_argument(
            "--disable-blink-features=AutomationControlled"
        )
        self.driver_options.add_argument("--window-size=1920,1080")

        # Дополнительные аргументы для лучшей маскировки
        self.driver_options.add_argument("--disable-gpu")
        self.driver_options.add_argument("--no-sandbox")
        self.driver_options.add_argument("--disable-dev-shm-usage")

    async def start_checking(self) -> None:
        """Запуск проверки всех ссылок"""
        try:
            links = await read_links()
            tasks = [self._check_product(link) for link in links]
            await asyncio.gather(*tasks)
        finally:
            session = await self.bot.get_session()
            await session.close()

    async def _check_product(self, link: Link) -> None:
        """Проверка одного продукта с использованием Chromium"""
        try:
            # Используем Chrome вместо Chrome, указывая options
            async with uc.Chrome(
                options=self.driver_options,
                browser_executable_path="/usr/bin/chromium",  # Указываем путь к Chromium
            ) as driver:
                driver.set_page_load_timeout(120)
                price_data = await self._get_price_data(driver, link.url)
                await self._process_price_changes(price_data, link)
        except Exception as ex:
            logger.error(f"Error checking {link.url}: {ex}")
            await self._notify_admin(f"[ERR] {link.url}: {ex}")

    async def _get_price_data(self, driver, url: str) -> dict:
        """Получение данных о цене со страницы"""
        driver.get(url)
        title = self._clean_title(driver.title)

        try:
            price_element = driver.find_element(
                By.CSS_SELECTOR, '[data-widget="webPrice"]'
            )
            attr = price_element.get_attribute("data-state")
            return {"title": title, "state": json.loads(attr), "url": url}
        except Exception as ex:
            logger.error(f"Price parsing error: {ex}")
            return {"title": title, "state": {}, "url": url, "error": str(ex)}

    def _clean_title(self, title: str) -> str:
        """Очистка заголовка от лишнего текста"""
        for text in config.text_for_replace_title:
            title = title.replace(text, "")
        return title.strip()

    async def _process_price_changes(self, data: dict, link: Link) -> None:
        """Обработка изменений цены"""
        price_info = self._extract_prices(data["state"])
        result = f"{data['title']} | Цена: {price_info['price']} р | Ozon: {price_info['ozon_price']} р"

        if self._has_price_changed(price_info, link):
            message = self._build_price_message(data["title"], price_info, link)
            await self._send_price_update(link.id, message)
            await update_price(
                Link(
                    id=link.id,
                    url=link.url,
                    price=price_info["price"],
                    price_ozon=price_info["ozon_price"],
                )
            )

        logger.info(result)

    def _extract_prices(self, state: dict) -> dict:
        """Извлечение цен из data-state"""
        return {
            "price": self._parse_price(state.get("price", "0")),
            "ozon_price": self._parse_price(state.get("cardPrice", "0")),
        }

    def _parse_price(self, price_str: str) -> int:
        """Парсинг цены из строки"""
        return int("".join(c for c in price_str if c.isdigit())) if price_str else 0

    def _has_price_changed(self, current_prices: dict, link: Link) -> bool:
        """Проверка изменения цены"""
        return (
            current_prices["price"] != link.price and current_prices["price"] != 0
        ) or (
            current_prices["ozon_price"] != link.price_ozon
            and current_prices["ozon_price"] != 0
        )

    def _build_price_message(self, title: str, prices: dict, link: Link) -> str:
        """Формирование сообщения об изменении цены"""
        message = [title]
        if link.price != 0 and prices["price"] != link.price:
            message.append(
                f"Старая цена: {link.price} руб\nНовая цена: {prices['price']} руб"
            )
        if link.price_ozon != 0 and prices["ozon_price"] != link.price_ozon:
            message.append(
                f"Старая цена Ozon: {link.price_ozon} руб\nНовая цена Ozon: {prices['ozon_price']} руб"
            )
        message.append(link.url)
        return "\n".join(message)

    async def _send_price_update(self, chat_id: int, message: str) -> None:
        """Отправка уведомления об изменении цены"""
        try:
            await self.bot.send_message(chat_id=chat_id, text=message)
        except Exception as ex:
            logger.error(f"Failed to send message to {chat_id}: {ex}")
            await self._notify_admin(f"[SEND ERR] {chat_id}: {ex}")

    async def _notify_admin(self, message: str) -> None:
        """Уведомление администратора об ошибке"""
        try:
            await self.bot.send_message(chat_id=TgKeys.admin_chatID, text=message)
        except Exception as ex:
            logger.error(f"Failed to notify admin: {ex}")
