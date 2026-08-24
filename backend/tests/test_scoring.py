from app.schemas import AwardPointRequest, CreateMatchRequest
from app.scoring import MatchService


def test_game_requires_two_point_margin() -> None:
    service = MatchService()
    match = service.create(CreateMatchRequest(player_one="A", player_two="B"))
    for _ in range(10):
        service.award_point(match.match_id, AwardPointRequest(player=0))
        service.award_point(match.match_id, AwardPointRequest(player=1))

    state = service.award_point(match.match_id, AwardPointRequest(player=0))
    assert state.points == (11, 10)
    assert state.games == (0, 0)

    state = service.award_point(match.match_id, AwardPointRequest(player=0))
    assert state.points == (0, 0)
    assert state.games == (1, 0)


def test_best_of_three_match_completion() -> None:
    service = MatchService()
    state = service.create(
        CreateMatchRequest(player_one="A", player_two="B", best_of=3)
    )
    for _ in range(22):
        state = service.award_point(state.match_id, AwardPointRequest(player=0))

    assert state.completed is True
    assert state.winner == "A"
    assert state.games == (2, 0)
