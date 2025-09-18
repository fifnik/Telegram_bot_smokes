from dataclasses import dataclass
import os


def _int_env(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


@dataclass(frozen=True)
class Settings:
    bot_token: str
    owner_id: int
    db_path: str


def load_settings() -> Settings:
    return Settings(
        bot_token=os.getenv("BOT_TOKEN", "7771944749:AAEOCHwAuSr7vEiwwGK_0tbPbSP7JFqjXD0"),
        owner_id=_int_env("OWNER_ID", 2082319342),
        db_path=os.getenv("DB_PATH", "smoke_idle.db"),
    )


settings = load_settings()
