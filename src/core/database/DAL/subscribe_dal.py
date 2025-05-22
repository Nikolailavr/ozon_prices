from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from core.database.models import Subscribe
from core.database.schemas import SubscribeBase


class SubscribeCRUD:
    @staticmethod
    async def get(session: AsyncSession, subscribe: SubscribeBase) -> Subscribe | None:
        stmt = select(Subscribe).filter(
            Subscribe.url == subscribe.url,
            Subscribe.telegram_id == subscribe.telegram_id,
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(
        session: AsyncSession,
        *,
        active: bool = None,
        telegram_id: int = None,
        url: str = None,
    ) -> list[Subscribe]:
        stmt = select(Subscribe)
        if active:
            stmt = select(Subscribe).where(Subscribe.active == active)
        if telegram_id:
            stmt = select(Subscribe).where(Subscribe.telegram_id == telegram_id)
        if url:
            stmt = select(Subscribe).where(Subscribe.url == url)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def create(session: AsyncSession, subscribe: SubscribeBase) -> Subscribe:
        new_subs = Subscribe(
            telegram_id=subscribe.telegram_id,
            url=subscribe.url,
            active=True,
        )
        session.add(new_subs)
        await session.commit()
        await session.refresh(new_subs)
        return new_subs

    @staticmethod
    async def delete(session: AsyncSession, subscribe: SubscribeBase) -> bool:
        stmt = delete(Subscribe).filter(
            Subscribe.url == subscribe.url,
            Subscribe.telegram_id == subscribe.telegram_id,
        )
        result = await session.execute(stmt)
        await session.commit()
        return result.rowcount > 0


subscribe_crud = SubscribeCRUD()
