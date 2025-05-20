import logging

from core.database.schemas.links import LinkBase

logger = logging.getLogger(__name__)


class Checker:
    async def check(
        self,
        link: LinkBase,
        link_old: LinkBase,
    ) -> LinkBase | None:
        """
        Обработка изменений цены
        """
        result = f"{link.title} | Цена: {link.price} р | Ozon: {link.ozon_price} р"
        if self._price_changed(link, link_old):
            logger.info(result)
            return link
        else:
            return None

    @staticmethod
    def _price_changed(
        link: LinkBase,
        link_old: LinkBase,
    ) -> bool:
        """
        Проверка изменения цены
        """
        return (link_old.price != link.price and link.price != 0) or (
            link_old.old_price != link.old_price and link.old_price != 0
        )
