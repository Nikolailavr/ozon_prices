import aiosqlite

import bot.misc.config as config
from bot.db.main import User


async def read_user(telegram_id: int) -> User:
    sql = f"""
        SELECT telegram_id, last_command FROM users
        WHERE telegram_id={telegram_id};"""
    async with aiosqlite.connect(config.SQLITE_DB_FILE) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(sql) as cursor:
            async for row in cursor:
                return User(
                            id=row["telegram_id"],
                            command=row["last_command"]
                            )


async def update_last_command(data: User) -> None:
    sql = """
        INSERT OR REPLACE INTO users 
            (telegram_id, last_command)
        VALUES (:telegram_id, :last_command);"""
    try:
        async with aiosqlite.connect(config.SQLITE_DB_FILE) as db:
            await db.execute(
                sql,
                {
                    "telegram_id": data.id,
                    "last_command": data.command,
                },
            )
            await db.commit()
    except Exception as ex:
        raise ex
