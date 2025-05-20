from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from core.database.models import User


class UserCRUD:
    @staticmethod
    async def get_user(session: AsyncSession, telegram_id: int) -> User | None:
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def create_user(
        session: AsyncSession,
        telegram_id: int,
    ) -> User:
        user = User(telegram_id=telegram_id)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    async def delete_user(
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

    async def update_last_command(
        self,
        session: AsyncSession,
        telegram_id: int,
        command: str,
    ) -> None:
        user = await self.get_user(session, telegram_id)
        if user:
            user.last_command = command
            await session.commit()


user_crud = UserCRUD()
