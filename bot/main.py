from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from aiogram import Bot
import time

from bot.misc import TgKeys, logger, current_price, driver_path, options, text_for_replace_title
from bot.db import read_links, update_price
from bot.db.main import Link


async def start_checking():
    bot = Bot(token=TgKeys.TOKEN, parse_mode='HTML')
    links = read_links()
    for link in links:
        await _checking(link=link.url, bot=bot)


async def _checking(link: Link, bot: Bot) -> None:
    html = ""
    title = ""
    s = Service(executable_path=driver_path)
    try:
        driver = webdriver.Chrome(service=s, options=options)
        driver.set_page_load_timeout(30)
    except Exception as ex:
        logger.error(ex)
        bot.send_message(chat_id=TgKeys.admin_chatID, text=f"[ERR] {ex}")
    else:
        try:
            await driver.get(url=link.url)
            time.sleep(1)
            html = driver.page_source
            title = driver.title.replace(text_for_replace_title, "")
        except Exception as ex:
            logger.error(ex)
        finally:
            driver.close()
            driver.quit()
        try:
            find_text = '<div id="state-webOzonAccountPrice'
            price_pos = html.find(find_text)
            find_text = '"{&quot;priceText&quot;:&quot;'
            price_pos = html.find(find_text, price_pos)
            last = html.find("₽", price_pos)
            price_temp = html[price_pos:last].replace(find_text, "").replace(" ", "")
            price = int(price_temp)
            if price != link.price:
                await bot.send_message(chat_id=link.id,
                                 text=f"{title}\nСтарая цена: {link.price} руб\nНовая цена: {price} руб\n{url}")
                update_price(data=link)
        except Exception as ex:
            logger.error(ex)
            await bot.send_message(chat_id=TgKeys.admin_chatID, text=f"[ERR] {ex}")