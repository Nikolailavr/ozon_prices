from core.database import db_helper
from core.database.models import Link
from core.database.DAL import link_crud
from core.database.schemas import LinkBase


class LinkService:
    @staticmethod
    async def get(
        url: str,
    ) -> Link:
        async with db_helper.get_session() as session:
            result = await link_crud.get(
                session,
                url,
            )
            return result

    @staticmethod
    async def update(link: LinkBase) -> Link | None:
        async with db_helper.get_session() as session:
            return await link_crud.update(
                session,
                link,
            )

    @staticmethod
    async def delete(url: str) -> bool:
        async with db_helper.get_session() as session:
            return await link_crud.delete(session, url)

    @staticmethod
    async def create(
        link: LinkBase,
    ) -> Link:
        async with db_helper.get_session() as session:
            return await link_crud.create_or_update_price(session, link)
