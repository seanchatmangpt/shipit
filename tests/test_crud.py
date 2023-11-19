# from datetime import datetime
#
# import pytest
# from sqlalchemy import create_engine
# from sqlmodel import Session
#
# from shipit.crud import *
# from shipit.models import *
#
#
# # Define tests for CRUD functions
# def test_create_event(session):
#     event = create_event(uid="12345", dtstamp=datetime.now(), dtstart=datetime.now(), summary="Test Event")
#     assert isinstance(event, Event)
#
#
# def test_read_event(session):
#     # Create an event
#     event_data = {
#         "uid": "12345",
#         "dtstamp": datetime.now(),
#         "dtstart": datetime.now(),
#         "summary": "Test Event",
#     }
#     new_event = create_event(**event_data)
#
#     # Read the event
#     event = read_event(event_id=new_event.id)
#     assert event is not None
#
#
# def test_update_event(session):
#     # Create an event
#     event_data = {
#         "uid": "12345",
#         "dtstamp": datetime.now(),
#         "dtstart": datetime.now(),
#         "summary": "Test Event",
#     }
#     new_event = create_event(**event_data)
#
#     event_data["summary"] = "Updated Event"
#
#     updated_event = update_event(event_id=new_event.id, **event_data)
#     assert updated_event.summary == "Updated Event"
#
#
# def test_delete_event(session):
#     # Create an event
#     event_data = {
#         "uid": "12345",
#         "dtstamp": datetime.now(),
#         "dtstart": datetime.now(),
#         "summary": "Test Event",
#     }
#     new_event = create_event(**event_data)
#
#     # Delete the event
#     delete_event(event_id=new_event.id)
#
#     # Ensure the event is deleted
#     event = read_event(event_id=new_event.id)
#     assert event is None
