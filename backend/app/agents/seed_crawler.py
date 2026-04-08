import asyncio
import logging
from typing import Any

from autogen import AssistantAgent

from app.core.config import settings
from app.core.tools import run_tinyfish_scrape

logger = logging.getLogger(__name__)

SEED_CRAWLER_SYSTEM_PROMPT = (
    "You are a seed crawler agent. Given a URL, use the TinyFish tool to scrape "
    "the page and extract: company name, description, key pages (about, team, "
    "contact, pricing, blog). Return a structured JSON object."
)

SEED_CRAWLER_GOAL = (
    "Extract company name, description, and key pages (about, team, contact, "
    "pricing, blog) as structured JSON."
)


class SeedCrawler:
    def __init__(self) -> None:
        self.agent = AssistantAgent(
            name="SeedCrawler",
            system_message=SEED_CRAWLER_SYSTEM_PROMPT,
            llm_config={
                "config_list": [
                    {
                        "model": "gpt-4o-mini",
                        "api_key": settings.openai_api_key or "",
                    }
                ]
            },
        )

    async def crawl(self, url: str) -> dict[str, Any]:
        if not url or not url.strip():
            raise ValueError("url is required.")

        logger.info("agent_start name=SeedCrawler url=%s", url.strip())
        raw_result = await asyncio.to_thread(
            run_tinyfish_scrape,
            url.strip(),
            SEED_CRAWLER_GOAL,
        )
        logger.info("agent_completed name=SeedCrawler url=%s", url.strip())
        if isinstance(raw_result, dict):
            return raw_result
        return {"raw_result": raw_result}


def crawl_seed_url(url: str) -> dict[str, Any]:
    """Sync helper for non-async callers."""
    crawler = SeedCrawler()
    return asyncio.run(crawler.crawl(url=url))
