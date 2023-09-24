import enum
from sqlalchemy import (
    update,
    Column, 
    Integer, 
    String, 
    Float, 
    Enum
)
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.settings import Base
from src.views.bets.schemas import EventState, EventsResponse


class BetStatus(enum.Enum):
    NEW = 1
    WIN = 2
    LOSE = 3


class Bet(Base):
    __tablename__ = "bets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(String)
    amount = Column(Float)
    status = Column(Enum(BetStatus))

    @staticmethod
    async def update_bets_statuses(
        async_session: AsyncSession,
        events_data: EventsResponse
    ):
        new_events = [event.event_id for event in events_data.root if event.state == EventState.NEW]
        finished_win_events = [event.event_id for event in events_data.root if event.state == EventState.FINISHED_WIN]
        finished_lose_events = [event.event_id for event in events_data.root if event.state == EventState.FINISHED_LOSE]
        async with async_session.begin():
            update_new_bets_stmt = (
                update(Bet)
                .where(Bet.event_id.in_(new_events))
                .values(status=BetStatus.NEW)
            )
            update_win_bets_stmt = ((
                update(Bet)
                .where(Bet.event_id.in_(finished_win_events))
                .values(status=BetStatus.WIN)
            ))
            update_lose_bets_stmt = ((update(Bet)
                .where(Bet.event_id.in_(finished_lose_events))
                .values(status=BetStatus.LOSE)
            ))

            await async_session.execute(update_new_bets_stmt)
            await async_session.execute(update_win_bets_stmt)
            await async_session.execute(update_lose_bets_stmt)
            await async_session.commit()

            
