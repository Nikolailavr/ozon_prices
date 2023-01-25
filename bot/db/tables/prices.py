import aiosqlite

import bot.misc.config as config
from bot.db.main import Link


async def update_price(data: Link) -> None:
    sql = f"""
        INSERT OR REPLACE INTO prices
        (url_link, price)
        VALUES (:url_link, :price);"""
    async with aiosqlite.connect(config.SQLITE_DB_FILE) as db:
        await db.execute(
            sql,
            {
                "url_link": data.url,
                "price": data.price,
            },
        )
        await db.commit()


# async def get_price(url: str) -> int:
#     sql = f"""
#         SELECT price IN prices
#         WHERE url_link={url};"""
#     async with aiosqlite.connect(config.SQLITE_DB_FILE) as db:
#         db.row_factory = aiosqlite.Row
#         async with db.execute(sql) as cursor:
#             async for row in cursor:
#                 if row["price"] is None: return 0
#                 else: return int(row["price"])
