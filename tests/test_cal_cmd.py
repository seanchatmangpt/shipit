import uuid

import pytest
from typer.testing import CliRunner
from datetime import datetime, timedelta
from sqlmodel import SQLModel, create_engine, Session
from shipit.models import Event  # Replace with your actual models import

runner = CliRunner()

# Mock database setup
TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(TEST_DATABASE_URL)


@pytest.fixture(name="mock_session")
def fixture_mock_session(mocker):
    mocker.patch("shipit.cli.get_session", return_value=Session(test_engine))


@pytest.fixture(autouse=True)
def setup_database():
    SQLModel.metadata.create_all(test_engine)
    yield
    SQLModel.metadata.drop_all(test_engine)


@pytest.fixture
def sample_events():
    events = [
        {
            "dtstart": datetime.now() - timedelta(days=1),
            "dtend": datetime.now() - timedelta(days=1, hours=1),
            "summary": "Past Event",
            # other fields
        },
        {
            "dtstart": datetime.now(),
            "dtend": datetime.now() + timedelta(hours=2),
            "summary": "Current Event",
            # other fields
        },
        {
            "dtstart": datetime.now() + timedelta(days=1),
            "dtend": datetime.now() + timedelta(days=1, hours=1),
            "summary": "Future Event",
            # other fields
        },
    ]
    with Session(test_engine) as session:
        for event_data in events:
            create_sample_event(session, **event_data)
    return events


def create_sample_event(session: Session, **kwargs):
    # Generate a unique identifier for the event
    uid = str(uuid.uuid4())
    dtstamp = datetime.utcnow()

    # Create the event with the generated UID and other provided fields
    event = Event(uid=uid, dtstamp=dtstamp, **kwargs)

    # Add and commit the event to the database
    session.add(event)
    session.commit()
    session.refresh(event)
    return event


def test_list_calendar_events_with_no_events(mock_session):
    result = runner.invoke(app, ["cal", "list"])
    assert result.exit_code == 0
    assert "No events found" in result.stdout


def test_list_calendar_events_with_events(mock_session, sample_events):
    result = runner.invoke(app, ["cal", "list"])
    assert result.exit_code == 0
    for event in sample_events:
        assert event["summary"] in result.stdout


def test_list_calendar_events_with_specific_date_range(mock_session, sample_events):
    start_date = datetime.now() - timedelta(days=2)
    end_date = datetime.now() + timedelta(days=2)
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")

    result = runner.invoke(
        app,
        [
            "cal",
            "list",
            "--start-datetime",
            start_date_str,
            "--end-datetime",
            end_date_str,
        ],
    )

    assert result.exit_code == 0
    assert "Past Event" in result.stdout
    assert "Current Event" in result.stdout
    assert "Future Event" in result.stdout


def test_list_calendar_events_with_invalid_date_range(mock_session):
    result = runner.invoke(
        app,
        [
            "cal",
            "list",
            "--start-datetime",
            "invalid-date",
            "--end-datetime",
            "invalid-date",
        ],
    )
    assert result.exit_code != 0
    assert (
        "Invalid date format" in result.stdout
    )  # Replace with your actual error message for invalid dates


# Add more tests as needed for different scenarios
