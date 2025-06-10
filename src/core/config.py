import logging
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, PostgresDsn, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

LOG_DEFAULT_FORMAT = (
    "[%(asctime)s] | %(module)20s:%(lineno)-4d | %(levelname)-8s - %(message)s"
)


class LoggingConfig(BaseModel):
    log_level: Literal[
        "debug",
        "info",
        "warning",
        "error",
        "critical",
    ] = "info"
    log_format: str = LOG_DEFAULT_FORMAT

    @property
    def log_level_value(self) -> int:
        return logging.getLevelNamesMapping()[self.log_level.upper()]


class DatabaseConfig(BaseModel):
    url: PostgresDsn
    echo: bool = False
    echo_pool: bool = False
    max_overflow: int = 10
    pool_size: int = 5

    naming_convention: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }


class Telegram(BaseModel):
    token: str
    admin_chat_id: int


class Parser(BaseModel):
    text_for_replace_title: tuple[str] = (
        " - купить по выгодным ценам в интернет-магазине OZON",
        " — купить в интернет-магазине OZON с быстрой доставкой",
        " - купить по доступным ценам в интернет-магазине OZON",
        " - купить по выгодной цене в интернет-магазине OZON",
    )
    driver_path: str = BASE_DIR / "chrome/chromedriver"
    example_url: str = BASE_DIR / "misc/example_url.png"


class Messages(BaseModel):
    HELP_MESSAGE: str = """
    Доступные команды бота:
    /help - показать список доступных команд
    /add - добавить новый url для подписки
    /list - показать список url в подписке
    /delete - удалить url из подписки
    """
    MSG_ADD: str = """Чтобы добавить новый url в подписку отправьте его в сообщении"""
    MSG_DELETE: str = """Чтобы удалить url из подписки отправьте его в сообщении"""
    BAD_MSG: str = "Я вас не понял, чтобы кзнать доступные команды наберите /help"
    BAD_URL: str = """Ваш url имеет неверный формат, пожалуйста, убедитесь что вы правильно скопировали ссылку на товар.
    Ваша ссылка должна начинаться с https://ozon.ru/"""
    GOOD_URL: str = """Ваш url успешно добавлен в подписку!"""
    GOOD_DELETE: str = """Ваш url успешно удален из подписки!"""
    CAPTION_EX_URL: str = (
        """Пример как правильно скопировать url (выделено синим цветом)"""
    )


class Celery(BaseModel):
    BROKER_URL: str
    RESULT_BACKEND: str


class Redis(BaseModel):
    HOST: str
    PORT: int
    PASSWORD: str


class Flower(BaseModel):
    user: str
    password: str


class Schedule(BaseModel):
    interval: int


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(
            BASE_DIR / ".env.template",
            BASE_DIR / ".env",
        ),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
    )
    logging: LoggingConfig = LoggingConfig()
    db: DatabaseConfig
    telegram: Telegram
    parser: Parser = Parser()
    msg: Messages = Messages()
    schedule: Schedule
    celery: Celery
    redis: Redis
    flower: Flower


settings = Settings()

# Logging
logging.basicConfig(
    level=settings.logging.log_level_value,
    format=settings.logging.log_format,
)
