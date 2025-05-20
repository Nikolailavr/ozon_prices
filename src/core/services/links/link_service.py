from core.database import db_helper
from core.database.models.links import Link, Price
from core.database.DAL import links_crud, prices_crud


class LinkService:
    @staticmethod
    async def add_user_link(
        telegram_id: int,
        url: str,
        initial_price: int = 0,
        initial_ozon_price: int = 0,
    ) -> tuple[Link, Price]:
        async with db_helper.get_session() as session:
            link = await links_crud.create_link(
                session,
                telegram_id,
                url,
            )
            price = await prices_crud.create_or_update_price(
                session,
                url,
                initial_price,
                initial_ozon_price,
            )
            return link, price

    @staticmethod
    async def get_user_links_with_prices(
        telegram_id: int,
    ) -> list[tuple[Link, Price]]:
        async with db_helper.get_session() as session:
            links = await links_crud.get_user_links(
                session,
                telegram_id,
            )
            result = []
            for link in links:
                price = await prices_crud.get_price(
                    session,
                    link.url_link,
                )
                if price:
                    result.append((link, price))
            return result

    @staticmethod
    async def update_link_prices(
        url: str,
        price: int | None = None,
        price_ozon: int | None = None,
    ) -> Price | None:
        async with db_helper.get_session() as session:
            return await prices_crud.update_price(
                session,
                url,
                price,
                price_ozon,
            )

    @staticmethod
    async def delete_user_link(url: str) -> bool:
        async with db_helper.get_session() as session:
            return await links_crud.delete_link(session, url)
