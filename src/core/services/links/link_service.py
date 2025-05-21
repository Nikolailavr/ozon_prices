from core.database import db_helper
from core.database.models.links import Link, Subscribe
from core.database.DAL import link_crud, subscribe_crud
from core.database.schemas.links import SubscribeCreate


class LinkService:
    @staticmethod
    async def add_subscribe(subscribe: SubscribeCreate) -> tuple[Link, Subscribe]:
        async with db_helper.get_session() as session:
            link = await subscribe_crud.create(session, subscribe)
            return link

    @staticmethod
    async def get_user_links_with_prices(
        telegram_id: int,
    ) -> list[tuple[Link, Subscribe]]:
        async with db_helper.get_session() as session:
            links = await link_crud.get_user_links(
                session,
                telegram_id,
            )
            result = []
            for link in links:
                price = await link_crud.get_price(
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
    ) -> Link | None:
        async with db_helper.get_session() as session:
            return await link_crud.update_price(
                session,
                url,
                price,
                price_ozon,
            )

    @staticmethod
    async def delete_user_link(url: str) -> bool:
        async with db_helper.get_session() as session:
            return await link_crud.delete_link(session, url)


link_service = LinkService()
