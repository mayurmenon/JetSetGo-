import asyncio
from typing import Any

from autogen import AssistantAgent
from app.core.config import settings


ORCHESTRATOR_SYSTEM_PROMPT = (
    "You are an orchestrator agent. Your job is to coordinate a team of specialist "
    "web scraping agents. Given a user's URL and research goal, you decide which "
    "specialists to dispatch, aggregate their results, and produce a final report."
)


class Orchestrator:
    def __init__(self) -> None:
        self.agent = AssistantAgent(
            name="Orchestrator",
            system_message=ORCHESTRATOR_SYSTEM_PROMPT,
            llm_config={
                "config_list": [
                    {
                        "model": "gpt-4o-mini",
                        "api_key": settings.openai_api_key or "",
                    }
                ]
            },
        )

    async def _seed_crawl(self, url: str, goal: str) -> dict[str, Any]:
        # Placeholder seed crawl stage (replace with TinyFish/AG2 tool call).
        await asyncio.sleep(0)
        return {
            "url": url,
            "goal": goal,
            "seed_pages": [url],
            "stage": "seed_crawl_completed",
        }

    async def _run_specialist(self, specialist_name: str, seed_data: dict[str, Any]) -> dict[str, Any]:
        # Placeholder specialist execution.
        await asyncio.sleep(0)
        return {
            "specialist": specialist_name,
            "status": "completed",
            "findings": f"{specialist_name} processed {seed_data['url']}",
        }

    async def run_pipeline(
        self,
        destination: str,
        start_date: str,
        end_date: str,
        budget: str,
        origin_city: str = None,
    ) -> dict:
        """Run the full trip planning pipeline."""
        from app.agents.seed_crawler import SeedCrawler
        from app.agents.specialists import TravelSpecialistFactory
        from app.agents.validator import Validator
        from app.agents.synthesis import SynthesisAgent

        # 1. Seed Crawler: Get destination overview
        seed = SeedCrawler()
        destination_guide_url = f"https://en.wikivoyage.org/wiki/{destination.replace(' ', '_')}"
        overview = await seed.crawl(destination_guide_url)

        # 2. Fan-out to specialists
        specialists = TravelSpecialistFactory()
        specialist_results = await specialists.dispatch_specialists(
            destination=destination,
            dates={"start": start_date, "end": end_date},
            budget=budget,
            origin=origin_city
        )

        # 3. Validate
        validator = Validator()
        validated_data = await validator.validate(specialist_results)

        # 4. Synthesize itinerary
        synthesizer = SynthesisAgent()
        itinerary = await synthesizer.synthesize(validated_data)

        return {"itinerary": itinerary, "raw_data": validated_data}


def run_orchestration(url: str, goal: str = "Extract structured web insights") -> dict[str, Any]:
    """Sync helper for environments that call orchestration without async support."""
    orchestrator = Orchestrator()
    return asyncio.run(orchestrator.run_pipeline(url=url, goal=goal))
