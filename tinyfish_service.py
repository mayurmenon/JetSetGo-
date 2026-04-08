import os

import httpx

from app.utils.logger import get_logger

logger = get_logger("tinyfish_service")


class TinyFishService:
    def __init__(self) -> None:
        self.api_key = os.getenv("TINYFISH_API_KEY", "")
        self.search_url = os.getenv("TINYFISH_SEARCH_URL", "https://api.search.tinyfish.ai")
        self.use_mock = os.getenv("USE_MOCK_TINYFISH", "true").lower() == "true"

    def _mock_data(self, destination: str, budget: float | None) -> dict:
        flights = [
            {
                "id": "f1",
                "title": f"SkyJet to {destination}",
                "price": 320.0,
                "currency": "USD",
                "rating": 4.3,
                "provider": "TinyFish Mock",
            },
            {
                "id": "f2",
                "title": f"AeroNova to {destination}",
                "price": 280.0 if not budget or budget > 300 else 240.0,
                "currency": "USD",
                "rating": 4.5,
                "provider": "TinyFish Mock",
            },
        ]

        accommodations = [
            {
                "id": "a1",
                "title": f"Urban Nest - {destination}",
                "price": 95.0,
                "currency": "USD",
                "rating": 4.2,
                "provider": "TinyFish Mock",
            },
            {
                "id": "a2",
                "title": f"Harbor Suites - {destination}",
                "price": 140.0,
                "currency": "USD",
                "rating": 4.7,
                "provider": "TinyFish Mock",
            },
        ]

        activities = [
            {
                "id": "t1",
                "title": f"Food Tour in {destination}",
                "price": 45.0,
                "currency": "USD",
                "rating": 4.8,
                "provider": "TinyFish Mock",
            },
            {
                "id": "t2",
                "title": f"City Museum Pass - {destination}",
                "price": 30.0,
                "currency": "USD",
                "rating": 4.4,
                "provider": "TinyFish Mock",
            },
        ]

        return {
            "flights": flights,
            "accommodations": accommodations,
            "activities": activities,
        }

    async def _call_tinyfish_search(self, query: str) -> list[dict]:
        headers = {
            "X-API-Key": self.api_key,
        }

        async with httpx.AsyncClient(timeout=8.0) as client:
            response = await client.get(
                self.search_url,
                headers=headers,
                params={"query": query},
            )
            response.raise_for_status()
            data = response.json()
            return data.get("results", [])

    async def fetch_recommendations(
        self,
        destination: str,
        dates: dict | None,
        budget: float | None,
        preferences: dict | None,
    ) -> dict:
        if self.use_mock or not self.api_key:
            return self._mock_data(destination, budget)

        try:
            flights_results = await self._call_tinyfish_search(f"best flight deals to {destination}")
            accommodations_results = await self._call_tinyfish_search(
                f"affordable accommodations in {destination}"
            )
            activities_results = await self._call_tinyfish_search(
                f"best activities and attractions in {destination}"
            )

            def to_deals(results: list[dict], prefix: str) -> list[dict]:
                # Search API returns web results; map them into our deal schema.
                mapped: list[dict] = []
                for idx, item in enumerate(results[:8], start=1):
                    mapped.append(
                        {
                            "id": f"{prefix}{idx}",
                            "title": item.get("title", "Untitled result"),
                            "price": 100.0 + idx * 25.0,  # placeholder until price source is available
                            "currency": "USD",
                            "rating": 4.0,
                            "provider": item.get("site_name", "TinyFish Search"),
                        }
                    )
                return mapped

            return {
                "flights": to_deals(flights_results, "f"),
                "accommodations": to_deals(accommodations_results, "a"),
                "activities": to_deals(activities_results, "t"),
            }
        except httpx.TimeoutException:
            logger.warning("TinyFish timeout; using mock fallback")
            return self._mock_data(destination, budget)
        except httpx.HTTPStatusError as exc:
            logger.warning("TinyFish HTTP error %s; using mock fallback", exc.response.status_code)
            return self._mock_data(destination, budget)
        except Exception as exc:
            logger.error("Unexpected TinyFish error: %s", str(exc))
            return self._mock_data(destination, budget)

