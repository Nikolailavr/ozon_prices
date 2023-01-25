from bot.misc import waitBar, logger
from bot import start_checking


if __name__ == '__main__':
    logger.info(" --- Start workinkg ozon telegram bot --- ")
    while True:
        try:
            logger.info("--- Checking ---")
            await start_checking()
            waitBar(10800)
        except KeyboardInterrupt:
            exit(1)
        except Exception as ex:
            logger.error(ex)

