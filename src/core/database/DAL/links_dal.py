from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from core.database.models import Link


class LinkCRUD:
    @staticmethod
    async def get_link(session: AsyncSession, url: str) -> Link | None:
        stmt = select(Link).where(Link.url_link == url)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_links(session: AsyncSession, telegram_id: int) -> list[Link]:
        stmt = select(Link).where(Link.telegram_id == telegram_id)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def create_link(session: AsyncSession, telegram_id: int, url: str) -> Link:
        link = Link(telegram_id=telegram_id, url_link=url)
        session.add(link)
        await session.commit()
        await session.refresh(link)
        return link

    @staticmethod
    async def delete_link(session: AsyncSession, url: str) -> bool:
        stmt = delete(Link).where(Link.url_link == url)
        result = await session.execute(stmt)
        await session.commit()
        return result.rowcount > 0


links_crud = LinkCRUD()
