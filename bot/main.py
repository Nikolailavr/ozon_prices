from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from aiogram import Bot
import asyncio
import json

from bot.misc import TgKeys, logger, config
from bot.db import read_links, update_price
from bot.db.main import Link


class Monitoring:
    def __init__(self):
        self.bot = Bot(token=TgKeys.TOKEN, parse_mode='HTML')

    async def start_checking(self) -> None:
        self.__init__()
        links = await read_links()
        tasks = [self._checking(link=link) for link in links]
        await asyncio.gather(*tasks)
        session = await self.bot.get_session()
        await session.close()

    async def _checking(self, link: Link) -> None:
        title = ""
        data_state = {}
        service = Service(executable_path=config.driver_path)
        try:
            driver = Chrome(service=service, options=config.options)
            driver.set_page_load_timeout(120)
        except Exception as ex:
            logger.error(ex)
            await self.bot.send_message(chat_id=TgKeys.admin_chatID,
                                        text=f"[ERR] {ex}")
        else:
            try:
                driver.get(url=link.url)
                title = driver.title
                # Убираем все лишнее из заголовка
                for each in config.text_for_replace_title:
                    title = title.replace(each, "")
                price_element = driver.find_element(
                    By.ID,
                    value='state-webPrice-3121879-default-1'
                )
                attr = price_element.get_attribute('data-state')
                data_state = json.loads(attr)
            except Exception as ex:
                logger.error(ex)
                await self.bot.send_message(chat_id=TgKeys.admin_chatID,
                                            text=f"[ERR] {ex}")
            finally:
                driver.close()
                driver.quit()
            # Find prices of items
            price_dict = await self._check_price(data_state, title=title,
                                                 link=link)
            if price_dict['msg_need']:
                await self.bot.send_message(chat_id=link.id,
                                            text=price_dict['text'])
            print(price_dict['result'])  # Вывод в консоль результата поиска

    async def _check_price(self, state: dict, title: str, link: Link):
        text = ''
        price_ozon = state.get('cardPrice', '0')
        price_ozon = self.get_only_digits(price_ozon)
        price = state.get('price', '0')
        price = self.get_only_digits(price)
        # Для отображения работы бота
        result = f'{title} | Цена: {price} р | Цена (Ozon): {price_ozon} р'
        msg_need = False
        if (price != link.price and price != 0) or \
           (price_ozon != link.price_ozon and price_ozon != 0):
            text = f"{title}\n"
            if link.price != 0:  # при изменении цены отправляем сообщение
                text += f"Старая цена: {link.price} руб\n" \
                        f"Новая цена: {price} руб\n"
                msg_need = True
            if link.price_ozon != 0:  # при изменении цены отправляем сообщение
                text += f"Старая цена (Ozon): {link.price_ozon} руб\n" \
                        f"Новая цена (Ozon): {price_ozon} руб\n"
                msg_need = True
            text += f"{link.url}"
            link.price = price
            link.price_ozon = price_ozon
            await update_price(link)
        return {'msg_need': msg_need, 'text': text, 'result': result}

    @staticmethod
    def get_only_digits(text: str):
        result = ''
        for el in text:
            if el.isdigit():
                result += el
        return int(result)
