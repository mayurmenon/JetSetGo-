import json
import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


def run_tinyfish_scrape(url: str, goal: str):
    """
    Execute a TinyFish scrape for a URL and extraction goal.

    Raises:
        ValueError: If required input is missing.
        RuntimeError: If TinyFish execution fails.
    """
    if not url or not url.strip():
        raise ValueError("url is required.")
    if not goal or not goal.strip():
        raise ValueError("goal is required.")

    logger.info("tinyfish_call_start url=%s", url.strip())
    return run_tinyfish_direct(url=url, goal=goal)


def run_tinyfish_direct(url: str, goal: str) -> dict:
    """
    Direct TinyFish fallback call using TinyFish SSE endpoint.

    Makes a POST request to:
    https://agent.tinyfish.ai/v1/automation/run-sse
    and parses streamed SSE events.
    """
    if not url or not url.strip():
        raise ValueError("url is required.")
    if not goal or not goal.strip():
        raise ValueError("goal is required.")

    endpoint = "https://agent.tinyfish.ai/v1/automation/run-sse"
    headers = {
        "X-API-Key": settings.tinyfish_api_key,
        "Content-Type": "application/json",
    }
    payload = {"url": url.strip(), "goal": goal.strip()}

    events: list[dict] = []
    latest_data: dict | str | None = None

    try:
        logger.info("tinyfish_direct_call_start url=%s endpoint=%s", url.strip(), endpoint)
        with httpx.Client(timeout=60.0) as client:
            with client.stream("POST", endpoint, headers=headers, json=payload) as response:
                response.raise_for_status()
                for raw_line in response.iter_lines():
                    line = (raw_line or "").strip()
                    if not line or not line.startswith("data:"):
                        continue

                    data_part = line[len("data:") :].strip()
                    if not data_part:
                        continue

                    try:
                        parsed = json.loads(data_part)
                    except json.JSONDecodeError:
                        parsed = data_part

                    event_entry = {"data": parsed}
                    events.append(event_entry)
                    latest_data = parsed

        result = {
            "status": "completed",
            "endpoint": endpoint,
            "events": events,
            "result": latest_data,
        }
        logger.info(
            "tinyfish_direct_call_completed url=%s events=%s",
            url.strip(),
            len(events),
        )
        return result
    except httpx.HTTPError as exc:
        logger.exception("tinyfish_direct_call_failed url=%s error=%s", url.strip(), exc)
        raise RuntimeError(f"TinyFish direct fallback failed: {exc}") from exc


def get_tool_registry() -> dict:
    """Return initialized tool instances used by agents."""
    return {"tinyfish_direct_fallback": run_tinyfish_direct}
