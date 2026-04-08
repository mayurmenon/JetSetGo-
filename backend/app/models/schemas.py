from typing import Any
from typing import Optional

from pydantic import BaseModel


class ScrapeRequest(BaseModel):
    destination: str
    start_date: str  # YYYY-MM-DD
    end_date: str  # YYYY-MM-DD
    budget: str  # "Budget", "Moderate", or "Luxury"
    origin_city: Optional[str] = None


class ScrapeResponse(BaseModel):
    job_id: str
    status: str
    result: dict[str, Any] | None = None


class AgentStatus(BaseModel):
    agent_name: str
    status: str
    message: str
