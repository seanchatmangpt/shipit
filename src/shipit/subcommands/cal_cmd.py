import ast
import asyncio
import csv
from datetime import timedelta
import io
from random import randint
from typing import Optional
from factory.faker import faker

Faker = faker.Faker()

import typer

from sqlmodel import select
from typer import Context

from shipit.cli import get_mem_store
from shipit.crud import *
from utils.agent_tools import select_and_execute_function, choose_function, execute_function
from utils.complete import acreate
from utils.models import ok_models
from utils.prompt_tools import prompt_map, prompt_dict

app = typer.Typer()


async def _chatbot(user_input):
    questions = [
        # "Come up with a start date and time for the event? Please provide DTSTART in YYYY-MM-DD HH:MM format.",
        # "Create a reasonable DTEND in YYYY-MM-DD HH:MM format. Please pay close attention to the amount of "
        # "time you are allocating for the event, DTEND",
        # "Guess the duration of the event. Please in a VEvent DURATION format.",
        # "Can you give me a SUMMARY for the event?",
        # "Create a DESCRIPTION. It should be a sentence or two.",
        # "Come up with a LOCATION for the event. Return None if not applicable."
        "What should we change the start time to in YYYY-MM-DD HH:MM format?",
    ]

    # base_prompt = f"Today is {str(datetime.now())}. " \
    #               f"You are a ICalendar Assistant. I need you to extract values for a icalendar VEVENT." \
    #               f"\n\n{user_input}\n"

    base_prompt = f"""You are a ICalendar Assistant. 
    Today is {str(datetime.now())}.
    Current calendar:
    {weeks(1)}
    I need you to extract values for a icalendar VEVENT.
    \n\n{user_input}\n
    """

    responses = await prompt_map(questions, base_prompt=base_prompt,
                                 # model_list=["text-davinci-003"],
                                 suffix="\n```vevent\n",
                                 stop=["\n"],
                                 temperature=0.0)

    args = "\n".join(responses[1:])

    prompt = f"You are a ICalendar Assistant. Today is {str(datetime.now())}\n" \
             f"Current calendar.\n{user_input}.\nThese are the values for the keyword arguments.\n{args}"

    function_list = [Event.create, Event.update, Event.delete]

    chosen_function = await choose_function(prompt, function_list)

    # print(prompt)

    if chosen_function == Event.create:
        await execute_function(prompt, Event.create)
    elif chosen_function == Event.update:
        chosen_event = Event.query(user_input)
        print(chosen_event)

    print(chosen_function)

    # Get the most recently modified event by Event.dtstamp
    # print(Event.most_recent())


async def _update_event(user_input):
    function_list = [Event.create, Event.update, Event.delete]

    chosen_function = await choose_function(user_input=user_input, function_list=function_list)

    print(chosen_function)

    chosen_event = Event.query(user_input)[0]

    questions = {"dtstart": "New DTSTART", "dtend": "New DTEND", "duration": "New validated DURATION",
                 "summary": "New SUMMARY is '", "description": "New DESCRIPTION is '", "location": "New LOCATION is '"}

    base_prompt = f"""You are a ICalendar Assistant. 
    Today is {str(datetime.now())}.
    Current calendar:
    {weeks(1)}
    I need you to extract values for a icalendar VEVENT.'
    
    {f"Updated event: {chosen_event}." if chosen_function == Event.update else ""}
    
    \n\n{user_input}\n
    
    """

    responses = await prompt_dict(questions, base_prompt=base_prompt,
                                  stop=["\n", "'"])

    correction_prompt = f"""You are a ICalendar Assistant.
    
    Updated event: {responses}. 
    
    Describe this to me when does it start, end, duration, 
    summary, description, and location? What information isn't correct? If it isn't "
    correct, what is the correct information?
    
    
    ```python\ncorrect_vevent_kwargs ={{"""

    corrected = await acreate(prompt=correction_prompt, stop=["\n\n"])

    kwargs = ast.literal_eval("{" + corrected)

    if chosen_function == Event.create:
        event = Event.create(**kwargs)
        print(event)
    elif chosen_function == Event.update:
        Event.update(event_id=chosen_event.id, **kwargs)


@app.command("bot")
def chatbot():
    user_input = typer.prompt("How can I assist you today?")
    # user_input = f"Make the code review session at {randint(1, 12)}pm on Tuesday"
    # asyncio.run(_chatbot(user_input))
    # chosen_event = Event.query(user_input)[0]
    asyncio.run(_update_event(user_input))



def create_test_events():
    now = datetime.now()
    events = [
        Event(
            id=1,
            uid="event-1",
            dtstamp=now,
            dtstart=now + timedelta(hours=1),
            dtend=now + timedelta(hours=2),
            duration="1 hour",
            summary="Morning Standup Meeting",
            description="Daily team standup meeting to discuss current progress and tasks.",
            location="Virtual Meeting Room"
        ),
        Event(
            id=2,
            uid="event-2",
            dtstamp=now,
            dtstart=now + timedelta(hours=3),
            dtend=now + timedelta(hours=5),
            duration="2 hours",
            summary="Code Review Session",
            description="Review recent code submissions and discuss improvements.",
            location="Conference Room B"
        ),
        Event(
            id=3,
            uid="event-3",
            dtstamp=now,
            dtstart=now + timedelta(hours=6),
            dtend=now + timedelta(hours=7, minutes=30),
            duration="1 hour 30 minutes",
            summary="Development Workshop",
            description="Interactive workshop on new development techniques.",
            location="Main Auditorium"
        )
    ]
    return events




@app.command("list")
def list_calendar_events(page: int = 0, page_size: int = 10):
    """List calendar events"""

    # print("Number of events:", len(events))  # Debugging statement
    print_events_as_csv(Event.get_by_page(page, page_size))

    # Execute the query and print events as CSV
    # print_events_as_csv(session.exec(query).all())

    # Get all events from the database
    # events = session.exec(select(Event)).all()
    # print_events_as_csv(events)


def print_events_as_csv(events):
    # Define the CSV file header and rows
    header = ["id", "summary", "dtstart", "dtend", "duration", "description", "location"]
    rows = []

    for event in events:
        # Convert datetime objects to formatted strings for CSV
        dtstart_str = event.dtstart.strftime("%Y-%m-%d %H:%M:%S")
        dtend_str = event.dtend.strftime("%Y-%m-%d %H:%M:%S") if event.dtend else ""

        # Create a row for each event
        row = [
            event.id,
            event.summary,
            dtstart_str,
            dtend_str,
            event.duration,
            event.description,
            event.location
        ]
        rows.append(row)

    # Create a StringIO object to hold the CSV data
    csv_buffer = io.StringIO()
    writer = csv.writer(csv_buffer)

    # Write the CSV data to the buffer
    writer.writerow(header)
    writer.writerows(rows)

    # Print the CSV data
    print(csv_buffer.getvalue())


if __name__ == "__main__":
    app()


def weeks(total=4):
    from datetime import datetime, timedelta

    # Define the start date (today) and end date (four weeks from now)
    start_date = datetime.now()
    end_date = start_date + timedelta(weeks=total)

    # Define the days of the week in Sun-Sat format
    days_of_week = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

    # Create a list to hold the dates and day names
    schedule = []

    # Generate the date range and populate the schedule list
    current_date = start_date
    while current_date <= end_date:
        row = [current_date.strftime("%Y-%m-%d"), days_of_week[current_date.weekday()]]
        schedule.append(row)
        current_date += timedelta(days=1)

    # Print the schedule to the console
    output = "Date       Day\n"
    for row in schedule:
        output += f"{row[0]}: {row[1]}\n"
    return output
