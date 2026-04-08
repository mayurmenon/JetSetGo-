import os

from app.models.search_models import SearchResponse
from app.services.cache_service import TTLCache
from app.services.ranking_service import rank_deals
from app.services.tinyfish_service import TinyFishService

cache_ttl = int(os.getenv("CACHE_TTL_SECONDS", "300"))
cache = TTLCache(ttl_seconds=cache_ttl)
tinyfish_service = TinyFishService()


async def search_travel(
    destination: str,
    dates: dict | None,
    budget: float | None,
    preferences: dict | None,
) -> SearchResponse:
    cache_key = {
        "destination": destination.strip().lower(),
        "dates": dates,
        "budget": budget,
    }

    cached = cache.get(cache_key)
    if cached:
        return SearchResponse(**{**cached, "cached": True})

    recommendations = await tinyfish_service.fetch_recommendations(
        destination=destination,
        dates=dates,
        budget=budget,
        preferences=preferences,
    )

    flights = rank_deals(recommendations.get("flights", []))
    accommodations = rank_deals(recommendations.get("accommodations", []))
    activities = rank_deals(recommendations.get("activities", []))

    result = {
        "destination": destination,
        "flights": flights,
        "accommodations": accommodations,
        "activities": activities,
        "cached": False,
    }

    cache.set(cache_key, result)
    return SearchResponse(**result)

