import decimal
import enum
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, RootModel


class FloatWithTwoDecimalPlaces(RootModel):
    root: str = Field(pattern=r"^\d+\.\d{2}$")


class EventState(enum.Enum):
    NEW = 1
    FINISHED_WIN = 2
    FINISHED_LOSE = 3


class Event(BaseModel):
    event_id: str
    coefficient: Optional[decimal.Decimal] = None
    deadline: Optional[int] = None
    state: Optional[EventState] = None


class EventsResponse(RootModel):
    root: list[Event]


class BetEntry(BaseModel):
    event_id: str
    amount: FloatWithTwoDecimalPlaces
    bet_status: Optional[EventState] = None


class BetStatus(enum.Enum):
    NEW = 1
    WIN = 2
    LOSE = 3


class BetModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    event_id: str
    amount: float
    status: BetStatus


class BetsList(RootModel):
    root: list[BetModel]
