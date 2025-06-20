from core.database.DAL import user_crud
from core.database.db_helper import db_helper
from core.database.schemas import UserRead


class UserService:
    @staticmethod
    async def get_or_create_user(telegram_id: int) -> UserRead:
        async with db_helper.get_session() as session:
            user = await user_crud.get_user(session, telegram_id)
            if not user:
                user = await user_crud.create(session, telegram_id)
            return user

    @staticmethod
    async def update(
        telegram_id: int,
        command: str = "",
        url: str = None,
        active: bool = False,
    ) -> None:
        async with db_helper.get_session() as session:
            await user_crud.update(
                session=session,
                new_user=UserRead(
                    telegram_id=telegram_id,
                    last_command=command,
                    url=url,
                    active=active,
                ),
            )

    @staticmethod
    async def get_all() -> list[UserRead]:
        async with db_helper.get_session() as session:
            users = await user_crud.get_all(session)
            return [
                UserRead.model_validate(user, from_attributes=True) for user in users
            ]


# user_service = UserService()
