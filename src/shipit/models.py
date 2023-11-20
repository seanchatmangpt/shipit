import json
import uuid

import openai
from dateutil import parser
from icontract import require, ensure
from sqlmodel import Field, SQLModel, Relationship, select
from datetime import datetime
from typing import Optional, List

from shipit.cli import get_session, get_mem_store
from utils.crud_tools import add_model, update_model, delete_model, get_model


def generate_embeddings(text):
    response = openai.embeddings.create(input=text, model="text-embedding-ada-002")
    return response.data[0]


class Calendar(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    prodid: str = Field(description="Product Identifier")
    version: str = Field(description="Version of the calendar")
    calscale: Optional[str] = Field(description="Calendar scale used")
    method: Optional[str] = Field(description="Method used in the calendar")
    events: List["Event"] = Relationship(back_populates="calendar")
    todos: List["Todo"] = Relationship(back_populates="calendar")
    journals: List["Journal"] = Relationship(back_populates="calendar")


class Event(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    uid: str = Field(description="Globally unique identifier")
    dtstamp: datetime = Field(description="Date/time stamp")
    dtstart: datetime = Field(description="Start date/time of the event")
    dtend: Optional[datetime] = Field(description="End date/time of the event")
    duration: Optional[str] = Field(description="Duration of the event")
    summary: Optional[str] = Field(description="Summary of the event")
    description: Optional[str] = Field(description="Full description of the event")
    location: Optional[str] = Field(description="Location of the event")
    calendar_id: Optional[int] = Field(default=None, foreign_key="calendar.id")
    calendar: Optional[Calendar] = Relationship(back_populates="events")
    alarms: List["Alarm"] = Relationship(back_populates="event")

    def __repr__(self):
        return f"Event(id={self.id}, summary='{self.summary}', dtstart={self.dtstart}, " \
               f"dtend={self.dtend}, duration={self.duration}, description='{self.description}', " \
               f"location='{self.location}')"

    def __str__(self):
        return f"Event(id={self.id}, summary='{self.summary}', dtstart='{str(self.dtstart)}', " \
               f"dtend='{str(self.dtend)}', duration={self.duration}, description='{self.description}', " \
               f"location='{self.location}')"

    @staticmethod
    @require(lambda dtstart: parser.parse(dtstart))
    @require(lambda dtend: dtend is None or parser.parse(dtend))
    @require(lambda duration: duration is None or isinstance(duration, str))
    @require(lambda summary: summary is None or isinstance(summary, str))
    @require(lambda description: description is None or isinstance(description, str))
    @require(lambda location: location is None or isinstance(location, str))
    @ensure(lambda result: result.id is not None)
    def create(
            dtstart: str,
            dtend: str = None,
            duration: str = None,
            summary: str = None,
            description: str = None,
            location: str = None,
    ) -> "Event":
        uid = uuid.uuid4()
        uid_str = str(uid)

        dtstamp = datetime.utcnow()

        event = Event(
            uid=uid_str,
            dtstamp=dtstamp,
            dtstart=parser.parse(dtstart),
            dtend=parser.parse(dtend) if dtend else None,
            duration=duration,
            summary=summary,
            description=description,
            location=location,
        )

        add_model(event)
        return event

    @staticmethod
    @require(lambda event_id: isinstance(event_id, int))
    @require(lambda dtstart: parser.parse(dtstart))
    @require(lambda dtend: dtend is None or parser.parse(dtend))
    @require(lambda duration: duration is None or isinstance(duration, str))
    @require(lambda summary: summary is None or isinstance(summary, str))
    @require(lambda description: description is None or isinstance(description, str))
    @require(lambda location: location is None or isinstance(location, str))
    # @ensure(lambda result: result.id is not None)
    def update(
            event_id: int,
            dtstart: str,
            dtend: str = None,
            duration: str = None,
            summary: str = None,
            description: str = None,
            location: str = None,
    ):
        with update_model(Event, event_id) as event:
            event.dtstamp = datetime.utcnow()
            event.dtstart = parser.parse(dtstart)
            event.dtend = parser.parse(dtend) if dtend else None
            event.duration = duration
            event.summary = summary
            event.description = description
            event.location = location

    @staticmethod
    @require(lambda event_id: isinstance(event_id, int))
    @ensure(lambda result, event_id: result is None)
    def delete(event_id: int) -> None:
        delete_model(Event, event_id)

    @staticmethod
    @require(lambda event_id: isinstance(event_id, int))
    @ensure(lambda result, event_id: result.id == event_id)
    def read(event_id: int) -> "Event":
        return get_model(Event, event_id)

    @staticmethod
    def most_recent() -> "Event":
        return get_session().exec(select(Event).order_by(Event.dtstamp.asc())).first()

    @staticmethod
    def get_by_page(page: int = 0, per_page: int = 10, sort: str = "dtstamp", asc: bool = True) -> List["Event"]:
        """Get events by page sorted by"""
        order_by = getattr(Event, sort).asc() if asc else getattr(Event, sort).desc()
        print(order_by, page, per_page, sort, asc)
        return get_session().exec(
            select(Event)
            .order_by(order_by)
            .offset(page * per_page)
            .limit(per_page)
        ).all()

    @staticmethod
    def query(text: str,
              where: dict = None,
              n_results: int = 10) -> List["Event"]:
        """Query events"""
        results = get_mem_store().query(collection_id="Event_collection", query=text, where=where, n_results=n_results)
        result_ids = [json.loads(r)['id'] for r in results['documents'][0]]
        models = get_session().exec(select(Event).where(Event.id.in_(result_ids))).all()
        # sort models by result_ids
        return sorted(models, key=lambda m: result_ids.index(m.id))


class Todo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    uid: str = Field(description="Globally unique identifier")
    dtstamp: datetime = Field(description="Date/time stamp")
    dtstart: Optional[datetime] = Field(description="Start date/time of the todo")
    due: Optional[datetime] = Field(description="Due date/time of the todo")
    summary: Optional[str] = Field(description="Summary of the todo")
    description: Optional[str] = Field(description="Description of the todo")
    completed: Optional[datetime] = Field(description="Completion date/time")
    calendar_id: Optional[int] = Field(default=None, foreign_key="calendar.id")
    calendar: Optional[Calendar] = Relationship(back_populates="todos")


class Journal(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    uid: str = Field(description="Globally unique identifier")
    dtstamp: datetime = Field(description="Date/time stamp")
    dtstart: Optional[datetime] = Field(
        description="Start date/time of the journal entry"
    )
    summary: Optional[str] = Field(description="Summary of the journal entry")
    description: Optional[str] = Field(description="Description of the journal entry")
    calendar_id: Optional[int] = Field(default=None, foreign_key="calendar.id")
    calendar: Optional[Calendar] = Relationship(back_populates="journals")


class Alarm(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    action: str = Field(description="Action of the alarm")
    trigger: datetime = Field(description="Trigger time of the alarm")
    duration: Optional[str] = Field(description="Duration of the alarm")
    repeat: Optional[int] = Field(description="Repeat count of the alarm")
    description: Optional[str] = Field(description="Description of the alarm")
    event_id: Optional[int] = Field(default=None, foreign_key="event.id")
    event: Optional[Event] = Relationship(back_populates="alarms")
