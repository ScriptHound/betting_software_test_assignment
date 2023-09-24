from sqlalchemy import delete, select

from src.models.bets import Bet, BetStatus
from src.views.bets.schemas import EventsResponse


async def test_bets_update(async_testing_session):
    # Arrange section
    async_testing_session.add(Bet(
        event_id="1",
        amount=100.00,
        status=BetStatus.NEW
    ))
    async_testing_session.add(Bet(
        event_id="2",
        amount=100.00,
        status=BetStatus.NEW
    ))
    async_testing_session.add(Bet(
        event_id="3",
        amount=100.00,
        status=BetStatus.WIN
    ))
    async_testing_session.add(Bet(
        event_id="4",
        amount=100.00,
        status=BetStatus.LOSE
    ))

    await async_testing_session.commit()
    events_data = EventsResponse.model_validate(
        [
            {
                "event_id": "1",
                "coefficient": 1.5,
                "deadline": 1000000000,
                "state": BetStatus.LOSE.value
            },
            {
                "event_id": "2",
                "coefficient": 1.5,
                "deadline": 1000000000,
                "state": BetStatus.WIN.value
            },
        ]
    )

    # Act section
    await Bet.update_bets_statuses(async_testing_session, events_data)

    try:
        all_bets_stmt = select(Bet)
        all_bets = await async_testing_session.execute(all_bets_stmt)
        all_bets = all_bets.scalars().all()
        print(all_bets)
        assert False
    finally:
        # Teardown section
        delete_stmt = delete(Bet)
        await async_testing_session.execute(delete_stmt)
        await async_testing_session.commit()


