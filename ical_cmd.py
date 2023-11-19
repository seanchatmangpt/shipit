# I am assuming you want to create a .ics file containing information of an event from a user input
# (i.e. a typer prompt)
# This file can be used to create a calendar event and store it in a calendar application

# Import the necessary modules
import datetime
from icalendar import Calendar, Event


# Create a function to ask user to input event information
def get_event_info():
    """Get event information from user input"""
    # Create an empty dictionary to store event information
    event_info = {}

    # Get event name from user
    event_name = input("Enter event name: ")
    event_info["summary"] = event_name

    # Get start date from user
    start_date = input("Enter start date (YYYY-MM-DD): ")
    # Convert start date string to datetime object
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    event_info["start"] = start_date

    # Get end date from user
    end_date = input("Enter end date (YYYY-MM-DD): ")
    # Convert end date string to datetime object
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    # Add one day to end date to include the whole day
    end_date += datetime.timedelta(days=1)
    event_info["end"] = end_date

    # Get location from user
    location = input("Enter location: ")
    event_info["location"] = location

    # Get description from user
    description = input("Enter description: ")
    event_info["description"] = description

    return event_info


# Create a function to create a .ics file from event information
def create_ics_file(event_info):
    """Create a .ics file from event information"""
    # Create a new Calendar object
    cal = Calendar()

    # Create a new Event object
    event = Event()

    # Add event information to the Event object
    event.add("summary", event_info["summary"])
    event.add("dtstart", event_info["start"])
    event.add("dtend", event_info["end"])
    event.add("location", event_info["location"])
    event.add("description", event_info["description"])

    # Add Event object to the Calendar object
    cal.add_component(event)

    # Create a file object to write the .ics file
    with open("event.ics", "wb") as f:
        # Write the Calendar object to the file
        f.write(cal.to_ical())

    # Print success message
    print("Event successfully created in event.ics file!")


# Get event information from user
event_info = get_event_info()

# Create a .ics file from event information
create_ics_file(event_info)
