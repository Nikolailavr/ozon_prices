import aiosqlite

from bot.db.main import Link
import bot.misc.config as config


async def read_links(telegram_id: int = None) -> list[Link]:
    links = list()
    sql = """
        SELECT l.url_link as url, p.price as price 
        FROM links as l
        LEFT JOIN prices p on l.url_link=p.url_link"""
    if telegram_id:
        sql += f"WHERE l.telegram_id={telegram_id}"
    sql += ";"
    # print(sql)
    async with aiosqlite.connect(config.SQLITE_DB_FILE) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(sql) as cursor:
            async for row in cursor:
                links.append(Link(
                    id=telegram_id,
                    url=row["url_link"],
                    price=int(row["price"]),
                ))
    return links


async def add_link(data: Link) -> None:
    sql = """
        INSERT INTO links
            (telegram_id, url_link)
        VALUES (:telegram_id, :url_link);"""
    try:
        async with aiosqlite.connect(config.SQLITE_DB_FILE) as db:
            await db.execute(
                sql,
                {
                    "telegram_id": data.id,
                    "url_link": data.url,
                },
            )
            await db.commit()
    except Exception as ex:
        raise ex


async def delete_link(data: Link) -> None:
    sql = f"""
        DELETE FROM links
        WHERE telegram_id={data.id} AND url_link={data.url};"""
    async with aiosqlite.connect(config.SQLITE_DB_FILE) as db:
        await db.execute(sql)
        await db.commit()
