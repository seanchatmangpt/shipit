import pytest
from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.pool import StaticPool
from shipit.models import *
import factory
from datetime import datetime, timedelta
from factory.faker import faker

Faker = faker.Faker()


# Database Fixtures
@pytest.fixture(scope="session")
def engine():
    return create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


@pytest.fixture(scope="session")
def create_all(engine):
    SQLModel.metadata.create_all(engine)


@pytest.fixture()
def session(engine, create_all):
    with Session(engine) as session:
        yield session


# Factory Definitions
class CalendarFactory(factory.Factory):
    class Meta:
        model = Calendar

    id = factory.Sequence(lambda n: n)
    prodid = Faker.pystr(max_chars=10)
    version = "2.0"
    calscale = Faker.word()
    method = Faker.word()


class EventFactory(factory.Factory):
    class Meta:
        model = Event

    id = factory.Sequence(lambda n: n)
    uid = Faker.uuid4()
    dtstamp = Faker.date_time_this_year()
    dtstart = Faker.date_time_this_year()
    dtend = factory.LazyAttribute(lambda o: o.dtstart + timedelta(hours=1))
    duration = str(Faker.time_delta(end_datetime=None))
    summary = Faker.sentence()
    description = Faker.text()
    location = Faker.address()
    calendar_id = factory.SelfAttribute("calendar.id")
    calendar = factory.SubFactory(CalendarFactory)


class TodoFactory(factory.Factory):
    class Meta:
        model = Todo

    id = factory.Sequence(lambda n: n)
    uid = Faker.uuid4()
    dtstamp = Faker.date_time_this_year()
    dtstart = Faker.date_time_this_year()
    due = Faker.future_date(end_date="+30d")
    summary = Faker.sentence()
    description = Faker.text()
    completed = Faker.boolean()
    calendar_id = factory.SelfAttribute("calendar.id")
    calendar = factory.SubFactory(CalendarFactory)


class JournalFactory(factory.Factory):
    class Meta:
        model = Journal

    id = factory.Sequence(lambda n: n)
    uid = Faker.uuid4()
    dtstamp = Faker.date_time_this_year()
    dtstart = Faker.date_time_this_year()
    summary = Faker.sentence()
    description = Faker.text()
    calendar_id = factory.SelfAttribute("calendar.id")
    calendar = factory.SubFactory(CalendarFactory)


class AlarmFactory(factory.Factory):
    class Meta:
        model = Alarm

    id = factory.Sequence(lambda n: n)
    action = Faker.word()
    trigger = Faker.date_time_this_month()
    duration = str(Faker.time_delta())
    repeat = Faker.pyint()
    description = Faker.sentence()
    event_id = factory.SelfAttribute("event.id")
    event = factory.SubFactory(EventFactory)
