from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from aiogram import Bot
import time

from bot.misc import TgKeys, logger, config
from bot.db import read_links, update_price
from bot.db.main import Link


async def start_checking() -> None:
    links = await read_links()
    for link in links:
        await _checking(link=link)


async def _checking(link: Link) -> None:
    bot = Bot(token=TgKeys.TOKEN, parse_mode='HTML')
    html = ""
    title = "Just a moment..."
    service = Service(executable_path=config.driver_path)
    try:
        driver = Chrome(service=service, options=config.options)
        driver.set_page_load_timeout(120)
    except Exception as ex:
        logger.error(ex)
        await bot.send_message(chat_id=TgKeys.admin_chatID, text=f"[ERR] {ex}")
    else:
        try:
            driver.get(url=link.url)
            html = driver.page_source
            title = driver.title
            # Убираем все лишнее из заголовка
            for each in config.text_for_replace_title:
                title = title.replace(each, "")
        except Exception as ex:
            logger.error(ex)
            await bot.send_message(chat_id=TgKeys.admin_chatID, text=f"[ERR] {ex}")
        finally:
            driver.close()
            driver.quit()
        # Find prices of items
        price_dict = await _check_price(html=html, title=title, link=link)
        if price_dict['msg_need']:
            await bot.send_message(chat_id=link.id, text=price_dict['text'])


async def _check_price(html: str, title: str, link: Link) -> dict:
    """
    Проверка изменения цены
    Возращает словарь для выдачи сообщения в телеграм
    {'msg_need': bool, 'text': str}
    """
    text = ''
    price = _find_price(html, config.find_price)
    price_ozon = _find_price(html, config.find_price_ozon)
    print(f'{title} | Цена: {price} р, Цена (Ozon): {price_ozon} р')  # Для отображения работы бота
    msg_need = False
    if price != link.price or price_ozon != link.price_ozon:
        text = f"{title}\n"
        if link.price != 0:  # Только при реальном изменении цены отправляем сообщение
            text += f"Старая цена: {link.price} руб\nНовая цена: {price} руб\n"
            msg_need = True
        if link.price_ozon != 0:  # Только при реальном изменении цены отправляем сообщение
            text += f"Старая цена (Ozon): {link.price_ozon} руб\nНовая цена (Ozon): {price_ozon} руб\n"
            msg_need = True
        text += f"{link.url}"
        link.price = price
        link.price_ozon = price_ozon
        await update_price(link=link)
    return {'msg_need': msg_need, 'text': text}


def _find_price(html: str, find_text: tuple) -> int:
    """
    Поиск цены в разметке html
    """
    price = 0
    price_pos = html.find(find_text[0])
    if price_pos != -1:
        price_pos = html.find(find_text[1], price_pos)
        last = html.find("₽", price_pos)
        price_temp = html[price_pos:last].replace(find_text[1], "").replace(" ", "")
        try:
            price = int(price_temp)
        except Exception as ex:
            logger.error(f'Price in not numeric: {ex}')
    return price
