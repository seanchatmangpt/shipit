import asyncio
import csv
from datetime import timedelta
import io
from typing import Optional

import typer

from sqlmodel import select
from typer import Context

from shipit.crud import *
from utils.agent_tools import select_and_execute_function, choose_function, execute_function
from utils.complete import acreate
from utils.models import ok_models
from utils.prompt_tools import prompt_map

app = typer.Typer()


async def _chatbot(user_input):
    questions = [
        "Come up with a start date and time for the event? Please provide DTSTART in YYYY-MM-DD HH:MM format.",
        "Create a reasonable DTEND in YYYY-MM-DD HH:MM format. Please pay close attention to the amount of "
        "time you are allocating for the event, Do not return DTSTART",
        "Guess the duration of the event. Please in a VEvent DURATION format.",
        "Can you give me a SUMMARY for the event?",
        "Create a DESCRIPTION. It should be a sentence or two.",
        "Come up with a LOCATION for the event. Return None if not applicable."
    ]

    base_prompt = f"Today is {str(datetime.now())}. " \
                  f"You are a ICalendar Assistant. I need you to extract values for a icalendar VEVENT." \
                  f"\n\n{user_input}\n"

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

    print(prompt)


    if chosen_function == Event.create:
        await execute_function(prompt, Event.create)
    elif chosen_function == Event.update:
        events = Event.get_by_page(0, 20)

        events_strs = [str(event) for event in events]

        # We are going to use a prompt_map to check if the
        # user wants to update the event.
        responses = await prompt_map(events_strs, base_prompt=f"{user_input}\nDoes this have anything to do with the event",
                                     # model_list=["text-davinci-003"],
                                     # suffix="\n```python\nis_event = ",
                                     # stop=["\n"],
                                     temperature=0.0)

        # zip the responses with the events
        # if the response is "True", then we will update the event
        for response, event in zip(responses, events):
            if "True" in response:
                event_id = event.id
                print(event_id)
                break

        print(responses)

    print(chosen_function)

    # Get the most recently modified event by Event.dtstamp
    # print(Event.most_recent())


@app.command("bot")
def chatbot():
    # user_input = typer.prompt("How can I assist you today?")
    user_input = "Update the sqlmodel event to thursday."
    asyncio.run(_chatbot(user_input))


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

    # questions = [
    #     "Guess is the start date and time for the event? Please provide DTSTART in YYYY-MM-DD HH:MM format.",
    #     "Guess the end date and time for the event? Please provide DTEND in YYYY-MM-DD HH:MM format. Do not return DTSTART",
    #     "Guess the duration of the event. Please in a VEvent DURATION format.",
    #     "Can you give me a SUMMARY for the event?",
    #     "Create a detailed DESCRIPTION of what the event is about?",
    #     "Where will the event take place? Please provide the LOCATION. Return None if not applicable."
    # ]
    #
    # user_input = f"I want to have a hour meeting with my team tomorrow at 10am at the office. Today is {str(datetime.now())}. " \
    #              f"You are a ICalendar Assistant. I need you to extract values for a icalendar VEVENT.\n"
    #
    #
    # responses = asyncio.run(
    #     prompt_map(questions, base_prompt=user_input,
    #                model_list=["text-davinci-003"],
    #                suffix="\n```vevent\n",
    #                stop=["\n"],
    #                temperature=0.0))
    #
    # prompt = f"You are a ICalendar Assistant. Today is {str(datetime.now())}\n" \
    #          f"Current calendar.\nI need you to {user_input}.\n{responses}" \
    #
    # print(responses)

    # function_list = [Event.create, Event.update, Event.delete]
    # asyncio.run(select_and_execute_function(prompt, function_list))
