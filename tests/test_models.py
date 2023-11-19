from tests.conftest import *
from shipit.models import *
from sqlmodel import select

from factory.faker import faker

Faker = faker.Faker()


def test_create_event_with_reminders(session):
    event = EventFactory()
    session.add(event)
    session.commit()

    assert session.get(Event, event.id) is not None

    alarm = AlarmFactory(event_id=event.id)
    session.add(alarm)
    session.commit()


def test_developer_busy_schedule(session):
    # Step 1: Create a calendar for the developer
    dev_calendar = CalendarFactory(prodid='dev-calendar', version='2.0')
    session.add(dev_calendar)
    session.commit()

    # Step 2: Add multiple events to the developer's calendar
    for _ in range(3):  # Adding 3 events for simplicity
        event = EventFactory(calendar=dev_calendar)  # Linking event to the developer's calendar
        session.add(event)

    # Step 3: Add todos for the developer
    for _ in range(2):  # Adding 2 todos
        todo = TodoFactory(calendar=dev_calendar)  # Linking todo to the developer's calendar
        session.add(todo)

    # Step 4: Add a journal entry
    journal_entry = JournalFactory(calendar=dev_calendar)  # Linking journal to the developer's calendar
    session.add(journal_entry)

    # Step 5: For each event, add an alarm and a reminder
    events = session.exec(select(Event).where(Event.calendar_id == dev_calendar.id)).all()
    for event in events:
        alarm = AlarmFactory(event=event)  # Linking alarm to the event
        session.add(alarm)

    session.commit()

    # Verification: Ensure all components are added correctly
    # Fetching all components linked to the developer's calendar
    events = session.exec(select(Event).where(Event.calendar_id == dev_calendar.id)).all()
    todos = session.exec(select(Todo).where(Todo.calendar_id == dev_calendar.id)).all()
    journals = session.exec(select(Journal).where(Journal.calendar_id == dev_calendar.id)).all()
    alarms = session.exec(select(Alarm).join(Event).where(Event.calendar_id == dev_calendar.id)).all()

    assert len(events) == 3  # Checking if 3 events were added
    assert len(todos) == 2  # Checking if 2 todos were added
    assert len(journals) == 1  # Checking if 1 journal entry was added
    assert len(alarms) == 3  # Checking if each event has an associated alarm
