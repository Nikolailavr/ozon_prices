from core.database import db_helper
from core.database.models import Link, Subscribe
from core.database.DAL import link_crud, subscribe_crud
from core.database.schemas import SubscribeBase


class SubscribeService:
    @staticmethod
    async def add(subscribe: SubscribeBase) -> Subscribe:
        async with db_helper.get_session() as session:
            new_subs = await subscribe_crud.create(session, subscribe)
            return new_subs

    @staticmethod
    async def get_all(
        telegram_id: int,
    ) -> list[Subscribe]:
        async with db_helper.get_session() as session:
            subscribes = await subscribe_crud.get_all(
                session,
                telegram_id,
            )
            return subscribes

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
    async def delete(subscribe: SubscribeBase) -> bool:
        async with db_helper.get_session() as session:
            return await subscribe_crud.delete(session, subscribe)


# subscribe_service = SubscribeService()
