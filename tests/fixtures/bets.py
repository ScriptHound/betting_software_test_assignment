import pytest

from sqlalchemy import delete, select
from src.models.bets import Bet
from src.views.bets.schemas import BetStatus


@pytest.fixture
async def bets_fixture(async_testing_session):
    async_testing_session.add(Bet(event_id="1", amount=100.00, status=BetStatus.NEW))
    async_testing_session.add(Bet(event_id="2", amount=100.00, status=BetStatus.NEW))
    async_testing_session.add(Bet(event_id="3", amount=100.00, status=BetStatus.WIN))
    async_testing_session.add(Bet(event_id="4", amount=100.00, status=BetStatus.LOSE))
    await async_testing_session.commit()

    try:
        bets_ids_stmt = select(Bet).order_by(Bet.id)
        bets_ids = await async_testing_session.execute(bets_ids_stmt)
        bets_ids = bets_ids.scalars().all()
        yield bets_ids
    finally:
        await async_testing_session.execute(delete(Bet))
        await async_testing_session.commit()
