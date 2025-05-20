import logging

from core import settings

logging.basicConfig(
    level=settings.logging.log_level_value,
    format=settings.logging.log_format,
)


def main(): ...


if __name__ == "__main__":
    main()
