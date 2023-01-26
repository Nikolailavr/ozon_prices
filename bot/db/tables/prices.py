import aiosqlite

import bot.misc.config as config
from bot.db.main import Link


async def update_price(link: Link) -> None:
    sql = """
        INSERT OR REPLACE INTO prices
        (url_link, price)
        VALUES (:url_link, :price);"""
    async with aiosqlite.connect(config.SQLITE_DB_FILE) as db:
        await db.execute(
            sql,
            {
                "url_link": link.url,
                "price": link.price,
            },
        )
        await db.commit()
