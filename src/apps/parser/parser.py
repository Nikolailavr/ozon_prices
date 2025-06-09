import asyncio
import json
import logging
import random
import time

import undetected_chromedriver as uc
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# from apps.bot import send_msg
from core import settings, redis_client, async_redis_client
from core.database.schemas import LinkBase
from core.services import SubscribeService
from apps.parser.checker import Checker

logger = logging.getLogger(__name__)

COOKIE_FILE = "ozon_cookies.json"


class Parser:
    def __init__(self):
        self.driver = None

    def login(self) -> bool | None:
        need_quit = None
        if self.driver is None:
            self._driver_run()
            need_quit = True
        try:
            self.__login()
            return True
        except Exception as ex:
            logger.error("Error: Login is not possible")
            raise ex
            # return None
        finally:
            if need_quit:
                self.driver.quit()

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
                # for sub in subs:
                #     await send_msg(
                #         chat_id=sub.telegram_id,
                #         text="Price is changed",
                #     )
        if need_quit:
            self.driver.quit()

    def _driver_run(self):
        try:
            options = uc.ChromeOptions()

            options.binary_location = "/usr/bin/chromium"
            # options.add_argument("--headless=new")
            options.debugger_address = "localhost:9222"
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")

            self.driver = uc.Chrome(options=options)
            self.driver.implicitly_wait(5)
            self.driver.set_page_load_timeout(120)
        except Exception as ex:
            logger.exception("Error in run driver")
            self.driver = None
            raise ex

    async def _get_url_data(self, url: str) -> LinkBase | None:
        try:
            loaded_cookies = await self.__load_cookies_if_exist()
            if loaded_cookies is None:
                logger.error("Error: Login is not possible")
                return None
            await asyncio.sleep(5)
            logger.info(f"Start loading {url}")
            self.driver.get(url)
            await asyncio.sleep(60)
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
            # await send_msg(
            #     chat_id=settings.telegram.admin_chat_id,
            #     text=f"Error get data from url {url}: {ex}",
            # )
            return None

    async def __load_cookies_if_exist(self) -> bool | None:
        cookies_json = await async_redis_client.get("cookies")
        if not cookies_json:
            logger.error("В Redis нет сохранённых cookies")
            # await send_msg(
            #     chat_id=settings.telegram.admin_chat_id,
            #     text=f"В Redis нет сохранённых cookies",
            # )
            return None
        self.driver.get("https://www.ozon.ru/my/main")
        time.sleep(10)
        cookies = json.loads(cookies_json)
        for cookie in cookies:
            try:
                cookie.pop("sameSite")
                self.driver.add_cookie(cookie)
            except Exception as ex:
                logger.warning(f"Can't add cookie {cookie.get('name')}: {ex}")
                return None

        logger.info("Cookies loaded into driver.")
        return True

    def __login(self):
        wait = WebDriverWait(self.driver, 20)
        # Открываем страницу регистрации
        self.driver.get("https://www.ozon.ru/my/main")
        time.sleep(10)
        logger.info(f"Title: {self.driver.title}")

        # Нажимаем кнопку "Войти или зарегистрироваться"
        logger.info('Нажимаем кнопку "Войти или зарегистрироваться"')
        login_button = wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'button[data-widget="loginButton"]')
            )
        )
        login_button.click()
        time.sleep(3)

        # Ждём, пока появится iframe с авторизацией
        logger.info("Ждём, пока появится iframe с авторизацией")
        WebDriverWait(self.driver, 10).until(
            EC.frame_to_be_available_and_switch_to_it((By.ID, "authFrame"))
        )

        # Кликаем по "Войти по почте"
        logger.info('Кликаем по "Войти по почте"')
        email_login_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//div[contains(text(), 'Войти по почте')]")
            )
        )
        email_login_button.click()

        # Вводим email
        logger.info("Вводим email")
        email_input = WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.ID, "email"))
        )
        email_input.send_keys("lavrovwrk@gmail.com")

        # Нажимаем кнопку "Войти"
        logger.info('Нажимаем кнопку "Войти"')
        submit_button = WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
        )
        submit_button.click()

        self.__waiting_code()

    def __waiting_code(self):
        logger.info("Ждём пока придёт код")
        code = None
        for _ in range(60):  # максимум 5 минут (60*5сек)
            code = redis_client.get("login_otp_code")
            if code:
                redis_client.delete("login_otp_code")
                self.__input_code(code)
                break
            time.sleep(5)
        if not code:
            logger.error("Код не получен, логин отменён")
            return

    def __input_code(self, code: str):
        input_field = self.driver.find_element(By.NAME, "otp")
        input_field.send_keys(code)

        cookies = self.driver.get_cookies()
        cookies_json = json.dumps(cookies, ensure_ascii=False)
        redis_client.set("cookies", cookies_json)

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


parser = Parser()


async def main():
    # parser.login()
    await parser.check("https://ozon.ru/t/3lSzd1G")


if __name__ == "__main__":
    asyncio.run(main())
