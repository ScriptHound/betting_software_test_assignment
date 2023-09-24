from fastapi import FastAPI, Depends, Body
from fastapi.responses import JSONResponse
import httpx
from src.database.settings import get_session
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.bets import Bet
from src.views.bets.logic import get_all_events_data_from_line_provider
from src.views.bets.schemas import BetEntry, EventsResponse


app = FastAPI()


async def get_http_client():
    async with httpx.AsyncClient() as client:
        yield client


@app.get("/events/")
async def get_all_bettable_events(
    http_client: httpx.AsyncClient = Depends(get_http_client)
):
    response = await get_all_events_data_from_line_provider(http_client)
    return response


@app.post("/bet/")
async def make_a_bet_on_event(
    bet_data: BetEntry = Body(),
    async_session: AsyncSession = Depends(get_session), # type: ignore
):
    bet = Bet(event_id=bet_data.event_id, amount=float(bet_data.amount.root))
    async_session.add(bet)
    await async_session.commit()
    await async_session.refresh(bet)
    response = {
        "bet_id": bet.id,
    }
    return JSONResponse(content=response, status_code=201)


@app.get("/bets/")
async def get_bets_history(
    http_client = Depends(get_http_client),
    session: AsyncSession = Depends(get_session)
):
    response = await get_all_events_data_from_line_provider(http_client)
    events_data = EventsResponse.model_validate(response)
    await Bet.update_bets_statuses(session, events_data)
