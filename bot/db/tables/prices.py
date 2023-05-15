import aiosqlite

from bot.db.main import Link
from bot.misc import config


async def update_price(link: Link) -> None:
    sql = """
        INSERT OR REPLACE INTO prices
        (url_link, price, price_ozon)
        VALUES (:url_link, :price, :price_ozon);"""
    async with aiosqlite.connect(config.SQLITE_DB_FILE) as db:
        await db.execute(
            sql,
            {
                "url_link": link.url,
                "price": link.price,
                "price_ozon": link.price_ozon,
            },
        )
        await db.commit()
