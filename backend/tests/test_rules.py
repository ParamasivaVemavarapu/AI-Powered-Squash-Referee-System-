import pytest

from app.rules import decide
from app.schemas import Decision, RallyObservation


@pytest.mark.parametrize(
    ("overrides", "expected"),
    [
        ({"observation_confidence": 0.4}, Decision.HUMAN_REVIEW),
        ({"serve_valid": False}, Decision.FAULT),
        ({"ball_hit_tin": True}, Decision.DOWN),
        ({"ball_out": True}, Decision.OUT),
        ({"bounce_count": 2}, Decision.DOUBLE_BOUNCE),
        (
            {
                "opponent_prevented_swing": True,
                "striker_had_direct_access": True,
            },
            Decision.STROKE,
        ),
        (
            {"interference": True, "striker_had_direct_access": True},
            Decision.YES_LET,
        ),
        (
            {"interference": True, "striker_had_direct_access": False},
            Decision.NO_LET,
        ),
        ({}, Decision.GOOD_RETURN),
    ],
)
def test_decision_precedence(overrides: dict, expected: Decision) -> None:
    observation = RallyObservation(rally_id="test-rally", **overrides)
    assert decide(observation).decision == expected


def test_low_confidence_requires_review() -> None:
    result = decide(
        RallyObservation(rally_id="uncertain", observation_confidence=0.64)
    )
    assert result.human_review_required is True
    assert result.evidence == ["low_observation_confidence"]
