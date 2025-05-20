from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.models.links import Price


class PriceCRUD:
    @staticmethod
    async def get_price(session: AsyncSession, url: str) -> Price | None:
        stmt = select(Price).where(Price.url_link == url)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def update_price(
        session: AsyncSession,
        url: str,
        price: int | None = None,
        price_ozon: int | None = None,
    ) -> Price | None:
        values = {}
        if price is not None:
            values["price"] = price
        if price_ozon is not None:
            values["price_ozon"] = price_ozon

        if not values:
            return None

        stmt = (
            update(Price).where(Price.url_link == url).values(**values).returning(Price)
        )
        result = await session.execute(stmt)
        await session.commit()
        return result.scalar_one_or_none()

    async def create_or_update_price(
        self,
        session: AsyncSession,
        url: str,
        price: int = 0,
        price_ozon: int = 0,
    ) -> Price:
        existing = await self.get_price(url)
        if existing:
            return await self.update_price(url, price, price_ozon)

        price_obj = Price(url_link=url, price=price, price_ozon=price_ozon)
        session.add(price_obj)
        await session.commit()
        await session.refresh(price_obj)
        return price_obj


prices_crud = PriceCRUD()
