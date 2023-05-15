import aiosqlite

from bot.db.main import Link
from bot.misc import config


async def read_links(telegram_id: int = None) -> list[Link]:
    links = list()
    sql = """
        SELECT l.telegram_id as id, l.url_link as url, p.price as price, p.price_ozon as price_ozon
        FROM links as l
        LEFT JOIN prices p on l.url_link=p.url_link"""
    if telegram_id:
        sql += f" WHERE l.telegram_id={telegram_id}"
    sql += ";"
    async with aiosqlite.connect(config.SQLITE_DB_FILE) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(sql) as cursor:
            async for row in cursor:
                links.append(Link(
                    id=row["id"],
                    url=row["url"],
                    price=int(row["price"]),
                    price_ozon=int(row["price_ozon"]),
                ))
    return links


async def add_link(link: Link) -> None:
    sql = """
        INSERT INTO links
            (telegram_id, url_link)
        VALUES (:telegram_id, :url_link);"""
    try:
        async with aiosqlite.connect(config.SQLITE_DB_FILE) as db:
            await db.execute(
                sql,
                {
                    "telegram_id": link.id,
                    "url_link": link.url,
                },
            )
            await db.commit()
    except Exception as ex:
        raise ex


async def delete_link(link: Link) -> None:
    sql = f"""
        DELETE FROM links
        WHERE telegram_id={link.id} AND url_link="{link.url}";"""
    async with aiosqlite.connect(config.SQLITE_DB_FILE) as db:
        await db.execute(sql)
        await db.commit()
