import logging
import os

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from app.rules import decide
from app.schemas import (
    AwardPointRequest,
    CreateMatchRequest,
    DecisionResponse,
    MatchState,
    RallyObservation,
)
from app.scoring import MatchCompletedError, MatchNotFoundError, MatchService

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("squash-referee")
matches = MatchService()

app = FastAPI(
    title="AI-Powered Squash Referee API",
    version="1.0.0",
    description="Explainable rally decisions and match scoring.",
)

origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root() -> dict[str, str]:
    return {"service": "squash-referee-api", "docs": "/docs", "health": "/health"}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy"}


@app.post("/api/v1/decisions", response_model=DecisionResponse)
def create_decision(observation: RallyObservation) -> DecisionResponse:
    result = decide(observation)
    logger.info(
        "decision rally_id=%s result=%s review=%s",
        result.rally_id,
        result.decision,
        result.human_review_required,
    )
    return result


@app.post(
    "/api/v1/matches",
    response_model=MatchState,
    status_code=status.HTTP_201_CREATED,
)
def create_match(request: CreateMatchRequest) -> MatchState:
    return matches.create(request)


@app.get("/api/v1/matches/{match_id}", response_model=MatchState)
def get_match(match_id: str) -> MatchState:
    try:
        return matches.get(match_id)
    except MatchNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Match not found.") from exc


@app.post("/api/v1/matches/{match_id}/points", response_model=MatchState)
def award_point(match_id: str, request: AwardPointRequest) -> MatchState:
    try:
        return matches.award_point(match_id, request)
    except MatchNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Match not found.") from exc
    except MatchCompletedError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
