import asyncio
import logging
from typing import Any

from autogen import AssistantAgent

from app.core.config import settings

logger = logging.getLogger(__name__)

VALIDATOR_SYSTEM_PROMPT = (
    "You are a data validator. You review scraped data from multiple agents and "
    "check for: contradictions, missing information, low-confidence fields. Flag "
    "any issues and produce a validation report."
)


class Validator:
    def __init__(self) -> None:
        self.agent = AssistantAgent(
            name="Validator",
            system_message=VALIDATOR_SYSTEM_PROMPT,
            llm_config={
                "config_list": [
                    {
                        "model": "gpt-4o-mini",
                        "api_key": settings.openai_api_key or "",
                    }
                ]
            },
        )

    async def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        logger.info("agent_start name=Validator")
        await asyncio.sleep(0)

        issues: list[dict[str, str]] = []
        if not data:
            issues.append({"type": "missing_data", "message": "No data received for validation."})

        specialist_results = data.get("specialist_results") or data.get("results") or []
        if not specialist_results:
            issues.append(
                {"type": "missing_information", "message": "No specialist outputs were provided."}
            )

        failed = [
            item.get("agent_name") or item.get("specialist")
            for item in specialist_results
            if item.get("status") in {"failed", "error"}
        ]
        if failed:
            issues.append(
                {
                    "type": "low_confidence",
                    "message": f"Some specialist runs failed: {', '.join(str(x) for x in failed)}",
                }
            )

        report = {
            "validator": self.agent.name,
            "is_valid": len(issues) == 0,
            "issues": issues,
            "summary": "Validation passed" if not issues else "Validation completed with issues",
        }
        logger.info("agent_completed name=Validator is_valid=%s issues=%s", report["is_valid"], len(issues))
        return {"validated": report["is_valid"], "validation_report": report, **data}


def validate_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Sync helper for legacy call sites."""
    validator = Validator()
    return asyncio.run(validator.validate(payload))
