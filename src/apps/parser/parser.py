import asyncio
import json
import logging
import time

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from tornado.httputil import HTTPInputError

# from apps.bot import send_msg
from core import redis_client, async_redis_client
from core.database.schemas import LinkBase
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
            self._driver_run()
            self.driver.quit()
        except Exception as ex:
            logger.error(ex)

    async def check(self, url: str):
        need_quit = False
        if self.driver is None:
            self._driver_run()
            need_quit = True
        logger.info(f"Start checking {url}")
        products = await self._get_url_data(url)
        if products:
            for item in products:
                new_link = await Checker.check_price_changing(item)
                # if new_link:
                #     subs = await SubscribeService.get_all(url=url)
        if need_quit:
            self.driver.quit()

    def _driver_run(self):
        try:
            options = uc.ChromeOptions()

            options.binary_location = "/usr/bin/chromium"
            # options.add_argument("--headless=new")
            # options.debugger_address = "localhost:9222"
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

    async def _get_url_data(self, url: str) -> list[LinkBase] | None:
        try:
            loaded_cookies = self.__load_cookies_if_exist()
            if loaded_cookies is None:
                logger.error("Error: Login is not possible")
                return None
            await asyncio.sleep(2)
            logger.info(f"Start loading {url}")
            self.driver.get(url)
            await asyncio.sleep(2)
            products = self._extract_products()
            return products
        except Exception as ex:
            logger.error(f"Error get data from url ({url}): {ex}")
            # await send_msg(
            #     chat_id=settings.telegram.admin_chat_id,
            #     text=f"Error get data from url {url}: {ex}",
            # )
            return None

    def __load_cookies_if_exist(self) -> bool | None:
        cookies_json = redis_client.get("cookies")
        if not cookies_json:
            logger.error("В Redis нет сохранённых cookies")
            # await send_msg(
            #     chat_id=settings.telegram.admin_chat_id,
            #     text=f"В Redis нет сохранённых cookies",
            # )
            return None
        self.driver.get("https://www.ozon.ru/my/main")
        time.sleep(3)
        if self.__check_antibot():
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
        return None

    def __login(self):
        wait = WebDriverWait(self.driver, 20)
        # Открываем страницу регистрации
        self.driver.get("https://www.ozon.ru/my/main")
        time.sleep(10)
        logger.info(f"Title: {self.driver.title}")
        if self.__check_antibot():
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
        else:
            raise HTTPInputError("Доступ ограничен")

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

        time.sleep(5)

        cookies = self.driver.get_cookies()
        cookies_json = json.dumps(cookies, ensure_ascii=False)
        redis_client.set("cookies", cookies_json)

    def _extract_products(self) -> list[LinkBase]:
        products = []
        # Получаем HTML-страницы через драйвер
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        # Находим все div с атрибутом data-state, содержащим карточки
        for div in soup.find_all("div", attrs={"data-state": True}):
            try:
                data_state = div["data-state"]
                state = json.loads(data_state)

                if "items" not in state or "tileLayout" not in state:
                    continue

                for item in state["items"]:
                    product = {}

                    # Ссылка
                    link = item.get("action", {}).get("link")
                    if link:
                        product["link"] = f"https://www.ozon.ru{link}"

                    # Цена и старая цена
                    for el in item.get("mainState", []):
                        if el.get("atom", {}).get("type") == "priceV2":
                            prices = el["atom"]["priceV2"]["price"]
                            product["price"] = next(
                                (
                                    p["text"]
                                    for p in prices
                                    if p["textStyle"] == "PRICE"
                                ),
                                None,
                            )
                            product["original_price"] = next(
                                (
                                    p["text"]
                                    for p in prices
                                    if p["textStyle"] == "ORIGINAL_PRICE"
                                ),
                                None,
                            )

                    # Название
                    for el in item.get("mainState", []):
                        if el.get("id", "") == "name":
                            product["title"] = el["atom"]["textAtom"].get("text")
                            break  # Берем первое вхождение (название идет в конце массива)

                    products.append(product)
                break

            except Exception as e:
                print(f"Ошибка при обработке карточки: {e}")
                continue

        return [
            LinkBase(
                url=product["link"],
                title=product["title"],
                ozon_price=product["price"],
                price=product["original_price"],
            )
            for product in products
        ]

    def __check_antibot(self) -> bool | None:
        ATTEMPT_COUNT = 10
        attempt = 0
        while (
            attempt < ATTEMPT_COUNT and self.driver.title.strip() == "Доступ ограничен"
        ):
            try:
                logger.info(f"Заголовок: {self.driver.title.strip()}")
                # Ждём появления кнопки "Обновить"
                refresh_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "reload-button"))
                )
                refresh_button.click()
                logger.info(f"Попытка №{attempt}. Нажал кнопку 'Обновить'")
            except Exception as ex:
                logger.error(f"Попытка №{attempt}. Не удалось обойти антибот защиту")
            finally:
                attempt += 1
                time.sleep(3)
        if attempt < ATTEMPT_COUNT:
            return True


parser = Parser()


async def main():
    # parser.login()
    await parser.check("https://ozon.ru/t/3lSzd1G")


if __name__ == "__main__":
    asyncio.run(main())
