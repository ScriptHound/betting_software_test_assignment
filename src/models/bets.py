import json
from sqlalchemy import select, update, Column, Integer, String, Float, Enum
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.settings import Base
from src.views.bets.schemas import BetModel, BetsList, EventState, EventsResponse
from src.views.bets.schemas import BetStatus


class Bet(Base):
    __tablename__ = "bets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(String)
    amount = Column(Float)
    status = Column(Enum(BetStatus), default=BetStatus.NEW)

    @staticmethod
    def serialize_bets(bets):
        bets_models = [BetModel.model_validate(bet) for bet in bets]
        bets_json = BetsList.model_validate(bets_models).model_dump_json()
        bets_json = json.loads(bets_json)
        return bets_json

    @staticmethod
    async def get_all_bets(async_session: AsyncSession):
        stmt = select(Bet)
        bets = await async_session.execute(stmt)
        bets = bets.scalars().all()
        return bets

    @staticmethod
    async def update_bets_statuses(
        async_session: AsyncSession, events_data: EventsResponse
    ):
        new_events = [
            event.event_id
            for event in events_data.root
            if event.state == EventState.NEW
        ]
        finished_win_events = [
            event.event_id
            for event in events_data.root
            if event.state == EventState.FINISHED_WIN
        ]
        finished_lose_events = [
            event.event_id
            for event in events_data.root
            if event.state == EventState.FINISHED_LOSE
        ]
        update_new_bets_stmt = (
            update(Bet).where(Bet.event_id.in_(new_events)).values(status=BetStatus.NEW)
        )
        update_win_bets_stmt = (
            update(Bet)
            .where(Bet.event_id.in_(finished_win_events))
            .values(status=BetStatus.WIN)
        )
        update_lose_bets_stmt = (
            update(Bet)
            .where(Bet.event_id.in_(finished_lose_events))
            .values(status=BetStatus.LOSE)
        )

        await async_session.execute(update_new_bets_stmt)
        await async_session.execute(update_win_bets_stmt)
        await async_session.execute(update_lose_bets_stmt)
        await async_session.commit()
