from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.models.links import Link
from core.database.schemas import LinkBase


class LinkCRUD:
    @staticmethod
    async def get(session: AsyncSession, url: str) -> Link | None:
        stmt = select(Link).where(Link.url == url)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def update(
        session: AsyncSession,
        link: LinkBase,
    ) -> Link | None:
        values = {}
        if link.price is not None:
            values["price"] = link.price
        if link.price_ozon is not None:
            values["price_ozon"] = link.price_ozon
        if not values:
            return None
        stmt = update(Link).where(Link.url == link.url).values(**values).returning(Link)
        result = await session.execute(stmt)
        await session.commit()
        return result.scalar_one_or_none()

    async def create_or_update_price(
        self, session: AsyncSession, link: LinkBase
    ) -> Link:
        existing = await self.get(session, link.url)
        if existing:
            return await self.update(session, link)
        price_obj = Link(url=link.url, price=link.price, price_ozon=link.price_ozon)
        session.add(price_obj)
        await session.commit()
        await session.refresh(price_obj)
        return price_obj

    @staticmethod
    async def delete(
        session: AsyncSession,
        url: str,
    ) -> bool:
        stmt = delete(Link).where(Link.url == url)
        result = await session.execute(stmt)
        await session.commit()
        return result.rowcount > 0


link_crud = LinkCRUD()
