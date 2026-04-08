import asyncio
import json
import logging
import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.agents.orchestrator import Orchestrator
from app.models.schemas import AgentStatus, ScrapeRequest, ScrapeResponse

router = APIRouter(tags=["scraping"])
logger = logging.getLogger(__name__)

jobs_store: dict[str, dict[str, Any]] = {}


def _new_job() -> dict[str, Any]:
    return {
        "status": "pending",
        "result": None,
        "events": [],
        "queue": asyncio.Queue(),
    }


async def _emit_event(job_id: str, event: AgentStatus) -> None:
    payload = event.model_dump()
    job = jobs_store[job_id]
    job["events"].append(payload)
    await job["queue"].put(payload)
    logger.info(
        "job_event job_id=%s agent=%s status=%s message=%s",
        job_id,
        payload["agent_name"],
        payload["status"],
        payload["message"],
    )


async def _run_pipeline(job_id: str, req: ScrapeRequest) -> None:
    job = jobs_store[job_id]

    try:
        logger.info(
            "pipeline_start job_id=%s destination=%s start=%s end=%s budget=%s origin=%s",
            job_id,
            req.destination,
            req.start_date,
            req.end_date,
            req.budget,
            req.origin_city,
        )
        job["status"] = "running"
        await _emit_event(
            job_id,
            AgentStatus(
                agent_name="Orchestrator",
                status="running",
                message="Pipeline started.",
            ),
        )

        orchestrator = Orchestrator()
        final_result = await orchestrator.run_pipeline(
            destination=req.destination,
            start_date=req.start_date,
            end_date=req.end_date,
            budget=req.budget,
            origin_city=req.origin_city,
        )
        job["result"] = final_result
        job["status"] = "completed"
        logger.info("pipeline_completed job_id=%s", job_id)
        await _emit_event(
            job_id,
            AgentStatus(agent_name="Orchestrator", status="completed", message="Pipeline complete."),
        )
    except Exception as exc:
        logger.exception("pipeline_failed job_id=%s error=%s", job_id, exc)
        job["status"] = "failed"
        job["result"] = {"error": str(exc)}
        await _emit_event(
            job_id,
            AgentStatus(agent_name="Orchestrator", status="failed", message=f"Pipeline failed: {exc}"),
        )
    finally:
        await job["queue"].put(None)


@router.get("/health")
def health() -> dict:
    logger.info("api_call endpoint=/health")
    return {"ok": True}


@router.post("/scrape", response_model=ScrapeResponse)
async def scrape(req: ScrapeRequest) -> ScrapeResponse:
    logger.info(
        "api_call endpoint=/scrape destination=%s start=%s end=%s budget=%s origin=%s",
        req.destination,
        req.start_date,
        req.end_date,
        req.budget,
        req.origin_city,
    )
    job_id = str(uuid.uuid4())
    jobs_store[job_id] = _new_job()
    asyncio.create_task(_run_pipeline(job_id=job_id, req=req))
    return ScrapeResponse(job_id=job_id, status="accepted", result=None)


@router.get("/scrape/{job_id}/stream")
async def stream_scrape(job_id: str) -> StreamingResponse:
    logger.info("api_call endpoint=/scrape/%s/stream", job_id)
    if job_id not in jobs_store:
        logger.warning("stream_job_not_found job_id=%s", job_id)
        raise HTTPException(status_code=404, detail="Job not found")

    async def event_generator():
        job = jobs_store[job_id]

        for event in job["events"]:
            yield f"data: {json.dumps(event)}\n\n"

        while True:
            event = await job["queue"].get()
            if event is None:
                break
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/scrape/{job_id}/result", response_model=ScrapeResponse)
def scrape_result(job_id: str) -> ScrapeResponse:
    logger.info("api_call endpoint=/scrape/%s/result", job_id)
    job = jobs_store.get(job_id)
    if not job:
        logger.warning("result_job_not_found job_id=%s", job_id)
        raise HTTPException(status_code=404, detail="Job not found")
    return ScrapeResponse(job_id=job_id, status=job["status"], result=job["result"])
