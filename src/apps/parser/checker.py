import logging

from core.database.schemas import LinkBase, LinkBig
from core.services import LinkService

logger = logging.getLogger(__name__)


class Checker:
    @staticmethod
    async def check_price_changing(
        link: LinkBase,
    ) -> LinkBig | None:
        """
        Обработка изменений цены
        """
        link_db = await LinkService.get(link.url)
        if link_db is None:
            await LinkService.create(link)
            data = link.model_dump()
            return LinkBig.model_validate(data)
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
            logger.info("Запись в БД успешна")
            data = link.model_dump()
            data.update(
                {
                    "ozon_price_old": link_db.ozon_price,
                    "price_old": link_db.price,
                }
            )
            return LinkBig.model_validate(data)
        else:
            return None
