from typing import Dict, AsyncGenerator
from datetime import datetime, timezone
import logging

from fastapi import Request, FastAPI, HTTPException
from pydantic import BaseModel
from starlette.concurrency import run_in_threadpool
from contextlib import asynccontextmanager

from model import moderate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("moderation")

LABEL_MAP = {
    "OK":  "not_offensive",
    "H":   "hate_speech",
    "H2":  "hate_with_threats",
    "V":   "violence",
    "V2":  "graphic_violence",
    "HR":  "harassment",
    "S":   "sexual_content",
    "S3":  "sexual_minors",
    "SH":  "self_harm",
}


class ModerateRequest(BaseModel):
    text: str


def moderate_named(text: str) -> Dict[str, float]:
    """Run moderation on `text` and return a mapping of friendly labels to scores."""
    raw = moderate(text)
    return {LABEL_MAP.get(label, label): score for label, score in raw.items()}


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    """
    Warm up the moderation pipeline once at startup to avoid cold-start latency.
    """
    await run_in_threadpool(moderate_named, "")
    yield


app = FastAPI(
    title="Content Moderation MVP",
    lifespan=lifespan
)


@app.get(
    "/healthz",
    summary="Health Check",
    description="Simple endpoint to verify the service is up."
)
async def healthz():
    """Health check endpoint returning service status."""
    return {"status": "ok"}


@app.middleware("http")
async def log_request_timestamp(request: Request, call_next):
    """Log an ISO-8601 UTC timestamp to the app logger after each incoming request."""
    response = await call_next(request)
    if request.url.path == "/moderate":
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
        logger.info(ts)

    return response


@app.post(
    "/moderate",
    response_model=Dict[str, float],
    summary="Run Content Moderation",
    description="Accepts JSON { text: string } and returns confidence scores for each moderation category."
)
async def moderate_endpoint(req: ModerateRequest):
    """Moderate `req.text` and return mapped scores, or a generic 500 on failure."""
    try:
        scores = await run_in_threadpool(moderate_named, req.text)
        return scores

    except Exception:
        logger.exception("Inference error during content moderation")
        raise HTTPException(
            status_code=500,
            detail="Internal error during content moderation. Please try again later."
        )
