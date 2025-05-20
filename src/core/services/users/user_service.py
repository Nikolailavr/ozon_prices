from core.database.DAL import user_crud
from core.database.db_helper import db_helper
from core.database.models import User


class UserService:
    @staticmethod
    async def get_or_create_user(telegram_id: int) -> User:
        async with db_helper.get_session() as session:
            user = await user_crud.get_user(session, telegram_id)
            if not user:
                user = await user_crud.create_user(session, telegram_id)
            return user

    @staticmethod
    async def update_last_command(telegram_id: int, command: str = "") -> None:
        async with db_helper.get_session() as session:
            await user_crud.update_last_command(
                session=session,
                telegram_id=telegram_id,
                command=command,
            )
