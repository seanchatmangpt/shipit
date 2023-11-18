import datetime
import subprocess
from typing import Optional

from icalendar import Calendar, Event
import typer
from pathlib import Path

app = typer.Typer()


def run_khal_command(command: str, *args: str) -> str:
    """Run a khal command and return its output."""
    process = subprocess.run(["khal", command, *args], capture_output=True, text=True)
    if process.returncode != 0:
        raise RuntimeError(f"khal command error: {process.stderr.strip()}")
    return process.stdout.strip()

@app.command()
def create_event(summary: str, start: str, end: str):
    """Create a new event."""
    output = run_khal_command("new", summary, start, end)
    typer.echo(output)

@app.command()
def list_events(day: Optional[str] = None):
    """List events."""
    args = [day] if day else []
    output = run_khal_command("list", *args)
    typer.echo(output)


@app.command()
def create():
    """Create an iCalendar event."""
    # Prompt for event details
    summary = typer.prompt("Enter event name")
    start = typer.prompt("Enter start date (YYYY-MM-DD)")
    end = typer.prompt("Enter end date (YYYY-MM-DD)")
    location = typer.prompt("Enter location")
    description = typer.prompt("Enter description")

    # Convert date strings to datetime objects
    start_date = datetime.datetime.strptime(start, "%Y-%m-%d")
    end_date = datetime.datetime.strptime(end, "%Y-%m-%d")

    # Create event
    event = Event()
    event.add("summary", summary)
    event.add("dtstart", start_date)
    event.add("dtend", end_date)
    event.add("location", location)
    event.add("description", description)

    # Create calendar
    cal = Calendar()
    cal.add_component(event)

    # Write to file
    file_path = Path.cwd() / f"{summary.replace(' ', '_')}.ics"
    with open(file_path, "wb") as f:
        f.write(cal.to_ical())

    typer.echo(f"Event created successfully: {file_path}")


if __name__ == "__main__":
    app()
