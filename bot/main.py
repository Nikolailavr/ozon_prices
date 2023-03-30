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
        driver.set_page_load_timeout(30)
        # options = ChromeOptions()
        # options.headless = True
        # driver = Chrome(use_subprocess=True, options=options)
    except Exception as ex:
        logger.error(ex)
        await bot.send_message(chat_id=TgKeys.admin_chatID, text=f"[ERR] {ex}")
    else:
        try:
            count = 0
            driver.get(url=link.url)
            html = driver.page_source
            title = driver.title.replace(config.text_for_replace_title, "")
            while title == 'Just a moment...' and count < 12:
                print(f'Попытка №{count}')
                time.sleep(10)
                count += 1
            with open(f"temp/{title[:10]}.txt", "w") as file:
                file.write(html)
        except Exception as ex:
            logger.error(ex)
            await bot.send_message(chat_id=TgKeys.admin_chatID, text=f"[ERR] {ex}")
        finally:
            driver.close()
            driver.quit()
        try:
            find_text = '<div id="state-webOzonAccountPrice'
            price_pos = html.find(find_text)
            if price_pos != -1:
                find_text = '"{&quot;priceText&quot;:&quot;'
                price_pos = html.find(find_text, price_pos)
                last = html.find("₽", price_pos)
                price_temp = html[price_pos:last].replace(find_text, "").replace(" ", "")
                price = int(price_temp)
                print(f'{title} | Цена: {price}')
                if price != link.price:
                    if link.price != 0:
                        text = f"{title}\nСтарая цена: {link.price} руб\nНовая цена: {price} руб\n{link.url}"
                        await bot.send_message(chat_id=link.id, text=text)
                    link.price = price
                    await update_price(link=link)
        except Exception as ex:
            logger.error(ex)
            await bot.send_message(chat_id=TgKeys.admin_chatID, text=f"[ERR] {ex}")
