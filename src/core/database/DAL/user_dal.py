from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from core.database.models import User
from core.database.schemas import UserRead


class UserCRUD:
    @staticmethod
    async def get_user(session: AsyncSession, telegram_id: int) -> UserRead | None:
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def create(
        session: AsyncSession,
        telegram_id: int,
    ) -> UserRead:
        user = User(telegram_id=telegram_id)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    async def delete(
        self,
        session: AsyncSession,
        user_id: int,
    ) -> bool:
        user = await self.get_user(session, user_id)
        if user:
            await session.delete(user)
            await session.commit()
            return True
        return False

    async def update(
        self,
        session: AsyncSession,
        new_user: UserRead,
    ):
        user = await self.get_user(session, new_user.telegram_id)
        if user:
            if user:
                updated = False

                if user.url != new_user.url:
                    user.url = new_user.url
                    updated = True

                if user.active != new_user.active:
                    user.active = new_user.active
                    updated = True

                if user.last_command != new_user.last_command:
                    user.last_command = new_user.last_command
                    updated = True

                if updated:
                    await session.commit()


user_crud = UserCRUD()
