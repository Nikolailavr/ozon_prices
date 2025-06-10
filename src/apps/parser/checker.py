import logging

from core.database.schemas import LinkBase
from core.services import LinkService

logger = logging.getLogger(__name__)


class Checker:
    @staticmethod
    async def check_price_changing(
        link: LinkBase,
    ) -> LinkBase | None:
        """
        Обработка изменений цены
        """
        link_db = await LinkService.get(link.url)
        if link_db is None:
            await LinkService.create(link)
            return link

        # Check changing price
        condition = (
            link_db.price != link.price,
            link_db.ozon_price != link.ozon_price,
        )
        if any(condition):
            logger.info(
                f"{link.title} | Цена: {link.price} р | Ozon: {link.ozon_price} р"
            )
            await LinkService.update(link)
            return link
        else:
            return None
