from datetime import UTC, datetime
from uuid import uuid4

from app.schemas import (
    AwardPointRequest,
    CreateMatchRequest,
    MatchEvent,
    MatchState,
)


class MatchNotFoundError(KeyError):
    pass


class MatchCompletedError(ValueError):
    pass


class MatchService:
    def __init__(self) -> None:
        self._matches: dict[str, MatchState] = {}

    def create(self, request: CreateMatchRequest) -> MatchState:
        match_id = str(uuid4())
        state = MatchState(
            match_id=match_id,
            players=(request.player_one, request.player_two),
            points=(0, 0),
            games=(0, 0),
            best_of=request.best_of,
            completed=False,
            winner=None,
            timeline=[
                MatchEvent(
                    sequence=1,
                    event_type="match_created",
                    message=f"{request.player_one} vs {request.player_two}",
                    created_at=datetime.now(UTC),
                )
            ],
        )
        self._matches[match_id] = state
        return state

    def get(self, match_id: str) -> MatchState:
        try:
            return self._matches[match_id]
        except KeyError as exc:
            raise MatchNotFoundError(match_id) from exc

    def award_point(self, match_id: str, request: AwardPointRequest) -> MatchState:
        state = self.get(match_id)
        if state.completed:
            raise MatchCompletedError("The match is already complete.")

        points = list(state.points)
        games = list(state.games)
        points[request.player] += 1
        game_won = points[request.player] >= 11 and (
            points[request.player] - points[1 - request.player] >= 2
        )
        message = f"Point to {state.players[request.player]}"

        if game_won:
            games[request.player] += 1
            points = [0, 0]
            message = f"Game to {state.players[request.player]}"

        games_needed = state.best_of // 2 + 1
        completed = games[request.player] >= games_needed
        winner = state.players[request.player] if completed else None
        if completed:
            message = f"Match to {winner}"

        event = MatchEvent(
            sequence=len(state.timeline) + 1,
            event_type="match_complete" if completed else "point_awarded",
            message=message,
            created_at=datetime.now(UTC),
        )
        updated = state.model_copy(
            update={
                "points": tuple(points),
                "games": tuple(games),
                "completed": completed,
                "winner": winner,
                "timeline": [*state.timeline, event],
            }
        )
        self._matches[match_id] = updated
        return updated
