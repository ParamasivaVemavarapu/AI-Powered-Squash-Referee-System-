from app.schemas import Decision, DecisionResponse, RallyObservation

REVIEW_THRESHOLD = 0.65


def decide(observation: RallyObservation) -> DecisionResponse:
    decision = Decision.GOOD_RETURN
    reason = "The rally observation contains no fault or interference condition."
    evidence: list[str] = []

    if observation.observation_confidence < REVIEW_THRESHOLD:
        decision = Decision.HUMAN_REVIEW
        reason = "Observation confidence is below the automatic-decision threshold."
        evidence = ["low_observation_confidence"]
    elif observation.serve_valid is False:
        decision = Decision.FAULT
        reason = "The serve was observed as invalid."
        evidence = ["invalid_serve"]
    elif observation.ball_hit_tin:
        decision = Decision.DOWN
        reason = "The ball contacted the tin."
        evidence = ["ball_hit_tin"]
    elif observation.ball_out:
        decision = Decision.OUT
        reason = "The ball contacted or crossed the out line."
        evidence = ["ball_out"]
    elif observation.bounce_count >= 2:
        decision = Decision.DOUBLE_BOUNCE
        reason = "The ball bounced at least twice before the return."
        evidence = ["bounce_count>=2"]
    elif observation.opponent_prevented_swing and (
        observation.striker_had_direct_access or observation.safety_risk
    ):
        decision = Decision.STROKE
        reason = (
            "The opponent prevented a direct swing and created a safety or access risk."
        )
        evidence = ["opponent_prevented_swing"]
        if observation.striker_had_direct_access:
            evidence.append("striker_had_direct_access")
        if observation.safety_risk:
            evidence.append("safety_risk")
    elif observation.interference and observation.striker_had_direct_access:
        decision = Decision.YES_LET
        reason = "Interference occurred while the striker had recoverable direct access."
        evidence = ["interference", "striker_had_direct_access"]
    elif observation.interference:
        decision = Decision.NO_LET
        reason = "Interference occurred without meaningful direct access to the ball."
        evidence = ["interference", "no_direct_access"]

    return DecisionResponse(
        rally_id=observation.rally_id,
        decision=decision,
        confidence=observation.observation_confidence,
        human_review_required=decision == Decision.HUMAN_REVIEW,
        reason=reason,
        evidence=evidence,
    )
