from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from aiogram import Bot
import time

from bot.misc import TgKeys, logger, config
from bot.db import read_links, update_price
from bot.db.main import Link


async def start_checking():
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
            count = 0
            driver.get(url=link.url)
            html = driver.page_source
            title = driver.title
            for each in config.text_for_replace_title:
                title = title.replace(each, "")
            time.sleep(1)
            while (title == 'Just a moment...' or title == 'Один момент…') and count < 18:
                print(f'Попытка №{count}')
                time.sleep(10)
                count += 1
        except Exception as ex:
            logger.error(ex)
            await bot.send_message(chat_id=TgKeys.admin_chatID, text=f"[ERR] {ex}")
        finally:
            driver.close()
            driver.quit()
        # Find prices of items
        price = find_price(html)
        price_ozon = find_ozon_price(html)
        print(f'{title} | Цена: {price} р, Цена (Ozon): {price_ozon} р')    # Для отображения работы бота
        msg_flag = False
        try:
            if price != link.price or price_ozon != link.price_ozon:
                text = f"{title}\n"
                if link.price != 0:     # Только при реальном изменении цены отправляем сообщение
                    text += f"Старая цена: {link.price} руб\nНовая цена: {price} руб\n"
                    msg_flag = True
                if link.price_ozon != 0:    # Только при реальном изменении цены отправляем сообщение
                    text += f"Старая цена (Ozon): {link.price_ozon} руб\nНовая цена (Ozon): {price_ozon} руб\n"
                    msg_flag = True
                text += f"{link.url}"
                if msg_flag:
                    await bot.send_message(chat_id=link.id, text=text)
                link.price = price
                link.price_ozon = price_ozon
                await update_price(link=link)
        except Exception as ex:
            logger.error(ex)
            await bot.send_message(chat_id=TgKeys.admin_chatID, text=f"[ERR] {ex}")


def find_price(html: str) -> int:
    price = 0
    find_text = '<span class="x1k kx2"><span>'
    price_pos = html.find(find_text)
    if price_pos != -1:
        last = html.find("₽", price_pos)
        price_temp = html[price_pos:last].replace(find_text, "").replace(" ", "")
        try:
            price = int(price_temp)
        except Exception as ex:
            logger.error(f'Price in not numeric: {ex}')
    return price


def find_ozon_price(html: str) -> int:
    price = 0
    find_text = '<div id="state-webOzonAccountPrice'
    price_pos = html.find(find_text)
    if price_pos != -1:
        find_text = '"{&quot;priceText&quot;:&quot;'
        price_pos = html.find(find_text, price_pos)
        last = html.find("₽", price_pos)
        price_temp = html[price_pos:last].replace(find_text, "").replace(" ", "")
        try:
            price = int(price_temp)
        except Exception as ex:
            logger.error(f'Price Ozon in not numeric: {ex}')
    return price
