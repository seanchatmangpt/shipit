# This is a placeholder for the python code for your job interview.

from typing import Optional
import typer
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

app = typer.Typer()

@app.command()
def create_event(name: str, start_time: str, end_time: str, description: Optional[str] = None):
    """
    Create a new event in the user's Google Calendar using the given parameters.
    :param name: The name of the event
    :param start_time: The start time of the event in ISO 8601 format
    :param end_time: The end time of the event in ISO 8601 format
    :param description: Optional description for the event
    """
    try:
        service = build('calendar', 'v3')
        event = {
            'summary': name,
            'start': {'dateTime': start_time},
            'end': {'dateTime': end_time},
            'description': description
        }
        service.events().insert(calendarId='primary', body=event).execute()
        typer.echo("Event created successfully!")
    except HttpError as e:
        typer.echo("Error creating event: {}".format(e))


if __name__ == "__main__":
    app()