from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class Decision(StrEnum):
    GOOD_RETURN = "good_return"
    FAULT = "fault"
    DOWN = "down"
    OUT = "out"
    DOUBLE_BOUNCE = "double_bounce"
    STROKE = "stroke"
    YES_LET = "yes_let"
    NO_LET = "no_let"
    HUMAN_REVIEW = "human_review"


class RallyObservation(BaseModel):
    rally_id: str = Field(min_length=1, max_length=100)
    serve_valid: bool | None = None
    ball_hit_tin: bool = False
    ball_out: bool = False
    bounce_count: int = Field(default=0, ge=0, le=5)
    interference: bool = False
    striker_had_direct_access: bool = True
    opponent_prevented_swing: bool = False
    safety_risk: bool = False
    observation_confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class DecisionResponse(BaseModel):
    rally_id: str
    decision: Decision
    confidence: float
    human_review_required: bool
    reason: str
    evidence: list[str]


class CreateMatchRequest(BaseModel):
    player_one: str = Field(min_length=1, max_length=80)
    player_two: str = Field(min_length=1, max_length=80)
    best_of: int = Field(default=5, ge=1, le=9)


class AwardPointRequest(BaseModel):
    player: int = Field(ge=0, le=1)
    decision: Decision | None = None
    rally_id: str | None = None


class MatchEvent(BaseModel):
    sequence: int
    event_type: str
    message: str
    created_at: datetime


class MatchState(BaseModel):
    match_id: str
    players: tuple[str, str]
    points: tuple[int, int]
    games: tuple[int, int]
    best_of: int
    completed: bool
    winner: str | None
    timeline: list[MatchEvent]
