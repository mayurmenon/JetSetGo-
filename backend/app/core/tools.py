import json
import logging
import time

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
    header_candidates = [
        {
            "X-API-Key": settings.tinyfish_api_key,
            "Content-Type": "application/json",
        },
        {
            "Authorization": f"Bearer {settings.tinyfish_api_key}",
            "Content-Type": "application/json",
        },
    ]
    payload = {"url": url.strip(), "goal": goal.strip()}

    events: list[dict] = []
    latest_data: dict | str | None = None

    logger.info("tinyfish_direct_call_start url=%s endpoint=%s", url.strip(), endpoint)
    last_error: Exception | None = None
    started_at = time.time()
    with httpx.Client(timeout=httpx.Timeout(30.0, connect=10.0, read=15.0)) as client:
        for idx, headers in enumerate(header_candidates):
            events.clear()
            latest_data = None
            try:
                with client.stream("POST", endpoint, headers=headers, json=payload) as response:
                    response.raise_for_status()
                    for raw_line in response.iter_lines():
                        if (time.time() - started_at) > 25:
                            logger.warning(
                                "tinyfish_direct_stream_timeout url=%s auth_mode=%s events=%s",
                                url.strip(),
                                "x-api-key" if idx == 0 else "bearer",
                                len(events),
                            )
                            break

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

                        # TinyFish SSE can remain open; return once we have enough data.
                        text_view = str(parsed).lower()
                        is_terminal = any(
                            marker in text_view for marker in ("completed", "complete", "done", "final")
                        )
                        if is_terminal or len(events) >= 3 or (time.time() - started_at) > 20:
                            break

                result = {
                    "status": "completed",
                    "endpoint": endpoint,
                    "events": events,
                    "result": latest_data,
                }
                logger.info(
                    "tinyfish_direct_call_completed url=%s events=%s auth_mode=%s",
                    url.strip(),
                    len(events),
                    "x-api-key" if idx == 0 else "bearer",
                )
                return result
            except httpx.HTTPStatusError as exc:
                body_text = exc.response.text if exc.response is not None else ""
                logger.warning(
                    "tinyfish_direct_auth_attempt_failed url=%s auth_mode=%s status=%s body=%s",
                    url.strip(),
                    "x-api-key" if idx == 0 else "bearer",
                    exc.response.status_code if exc.response is not None else "unknown",
                    body_text[:500],
                )
                last_error = RuntimeError(
                    f"TinyFish auth failed ({exc.response.status_code}): {body_text[:500]}"
                )
            except Exception as exc:
                logger.exception("tinyfish_direct_call_failed url=%s error=%s", url.strip(), exc)
                last_error = exc

    raise RuntimeError(f"TinyFish direct fallback failed: {last_error}")


def get_tool_registry() -> dict:
    """Return initialized tool instances used by agents."""
    return {"tinyfish_direct_fallback": run_tinyfish_direct}
