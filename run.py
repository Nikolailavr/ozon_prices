import asyncio

from bot.misc import waitBar, logger
from bot import Monitoring


if __name__ == '__main__':
    logger.info(" --- Start workinkg ozon telegram bot --- ")
    parser = Monitoring()
    while True:
        logger.info("--- Checking ---")
        try:
            asyncio.run(parser.start_checking())
        except KeyboardInterrupt:
            exit(1)
        except Exception as ex:
            logger.error(ex)
        waitBar(10800)

