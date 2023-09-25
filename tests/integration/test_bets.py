from sqlalchemy import select

from src.models.bets import Bet
from src.views.bets.schemas import BetStatus, EventsResponse


async def test_bets_update(async_testing_session, bets_fixture):
    # Arrange section
    events_data = EventsResponse.model_validate(
        [
            {
                "event_id": "1",
                "coefficient": 1.5,
                "deadline": 1000000000,
                "state": BetStatus.LOSE.value,
            },
            {
                "event_id": "2",
                "coefficient": 1.5,
                "deadline": 1000000000,
                "state": BetStatus.WIN.value,
            },
        ]
    )
    expected_statuses_and_event_ids = [
        ("1", BetStatus.LOSE),
        ("2", BetStatus.WIN),
        ("3", BetStatus.WIN),
        ("4", BetStatus.LOSE),
    ]

    await Bet.update_bets_statuses(async_testing_session, events_data)

    all_bets_stmt = select(Bet.event_id, Bet.status)
    all_bets = await async_testing_session.execute(all_bets_stmt)
    all_bets = all_bets.all()
    all_bets.sort(key=lambda x: x[0])
    assert all_bets == expected_statuses_and_event_ids


async def test_get_all_bets(async_testing_session, bets_fixture):
    expected_json = [
        {
            "id": bets_fixture[0].id,
            "event_id": "1",
            "amount": 100.0,
            "status": BetStatus.NEW.value,
        },
        {
            "id": bets_fixture[1].id,
            "event_id": "2",
            "amount": 100.0,
            "status": BetStatus.NEW.value,
        },
        {
            "id": bets_fixture[2].id,
            "event_id": "3",
            "amount": 100.0,
            "status": BetStatus.WIN.value,
        },
        {
            "id": bets_fixture[3].id,
            "event_id": "4",
            "amount": 100.0,
            "status": BetStatus.LOSE.value,
        },
    ]

    bets = await Bet.get_all_bets(async_testing_session)
    assert len(bets) == 4
    bets_json = Bet.serialize_bets(bets)
    assert bets_json == expected_json
