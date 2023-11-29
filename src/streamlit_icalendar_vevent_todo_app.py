import streamlit as st
import icalendar
import vevent
import todo
from streamlit import multi_page

def create_python():
  """
  Use streamlit to create a multi-page python app that generates vevent todo items and exports them to an icalendar file.
  """
  # Use st.title() to create the title of the app
  st.title("Python Assistant - Create VEvent Todo App")

  # Use st.sidebar to create a sidebar for navigation
  st.sidebar.title("Navigation")
  # Use st.sidebar.radio() to create a radio button for selecting pages
  page = st.sidebar.radio("Select Page", ["Create VEvent Todo", "Export iCalendar"])

  # Use multi_page() to create the multi-page app
  multi_page(page)

  # If page is "Create VEvent Todo"
  if page == "Create VEvent Todo":
    # Use st.subheader() to create a subheader for the page
    st.subheader("Create VEvent Todo")
    # Use st.text_input() to get input for the event title
    event_title = st.text_input("Event Title")

    # Use st.date_input() to get input for the event date
    event_date = st.date_input("Event Date")

    # Use st.time_input() to get input for the event start time
    event_start_time = st.time_input("Event Start Time")

    # Use st.time_input() to get input for the event end time
    event_end_time = st.time_input("Event End Time")

    # Use st.selectbox() to get input for the event priority
    event_priority = st.selectbox("Event Priority", [1, 2, 3, 4, 5])

    # Use st.button() to create a button to add the event to the icalendar
    if st.button("Add Event"):
      # Create a vevent todo item with the given inputs
      vevent_todo = vevent.Todo()
      vevent_todo.add('summary', event_title)
      vevent_todo.add('dtstart', event_date + event_start_time)
      vevent_todo.add('dtend', event_date + event_end_time)
      vevent_todo.add('priority', event_priority)

      # Create an icalendar file with the vevent todo item
      ical_file = icalendar.Calendar()
      ical_file.add_component(vevent_todo)

      # Use st.success() to display a success message
      st.success("VEvent Todo successfully added to iCalendar!")

  # If page is "Export iCalendar"
  elif page == "Export iCalendar":
    # Use st.subheader() to create a subheader for the page
    st.subheader("Export iCalendar")

    # Use st.file_uploader() to upload an icalendar file
    ical_file = st.file_uploader("Upload iCalendar File", type="ics")

    # If ical_file is not None
    if ical_file is not None:
      # Use st.success() to display a success message
      st.success("iCalendar successfully exported!")

      # Use st.download_button() to create a button to download the icalendar file
      st.download_button("Download iCalendar", data=ical_file, file_name="event.ics")
    
# Run the create_python() function
create_python()