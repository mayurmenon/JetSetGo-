import logging
import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

# Load variables from backend/.env when present.
load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env")


def configure_logging() -> None:
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO").upper(),
        format=(
            "%(asctime)s | %(levelname)s | %(name)s | "
            "event=%(message)s"
        ),
    )


@dataclass(frozen=True)
class Settings:
    openai_api_key: str | None
    tinyfish_api_key: str
    api_prefix: str = "/api"

    @property
    def OPENAI_API_KEY(self) -> str | None:
        """Compatibility alias for modules using uppercase setting name."""
        return self.openai_api_key

    @classmethod
    def from_env(cls) -> "Settings":
        openai_api_key = (os.getenv("OPENAI_API_KEY") or "").strip() or None
        tinyfish_api_key = (os.getenv("TINYFISH_API_KEY") or "").strip()

        missing = []
        if not tinyfish_api_key:
            missing.append("TINYFISH_API_KEY")

        if missing:
            missing_keys = ", ".join(missing)
            raise ValueError(f"Missing required environment variables: {missing_keys}")

        return cls(
            openai_api_key=openai_api_key,
            tinyfish_api_key=tinyfish_api_key,
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings.from_env()


configure_logging()
settings = get_settings()
