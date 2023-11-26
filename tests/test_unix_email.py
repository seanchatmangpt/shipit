import pytest
from shipit.unix_email import UnixEmailSystem  # Replace 'your_module' with the actual module name

@pytest.fixture
def email_system():
    return UnixEmailSystem()

def test_register_user(email_system):
    email_system.register_user("user@example.com")
    assert "user@example.com" in email_system.users

def test_create_and_get_mailing_list(email_system):
    email_system.create_mailing_list("team_a", ["alice@example.com", "bob@example.com"])
    members = email_system.get_mailing_list_members("team_a")
    assert members == ["alice@example.com", "bob@example.com"]

def test_send_group_message(email_system):
    email_system.register_user("alice@example.com")
    email_system.register_user("bob@example.com")
    email_system.create_mailing_list("team_a", ["alice@example.com", "bob@example.com"])

    sender = "charlie@example.com"
    subject = "Team Meeting"
    body = "Team meeting at 2 PM today."

    email_system.send_email(sender, to_emails=["team_a"], subject=subject, body=body)

    alice_inbox = email_system.get_emails("alice@example.com")
    bob_inbox = email_system.get_emails("bob@example.com")

    assert len(alice_inbox) == 1
    assert len(bob_inbox) == 1

    assert f"From: {sender}" in alice_inbox[0]
    assert f"From: {sender}" in bob_inbox[0]

def test_send_individual_message(email_system):
    email_system.register_user("alice@example.com")
    email_system.register_user("charlie@example.com")

    sender = "charlie@example.com"
    subject = "Private Message"
    body = "Hi Alice, this is a private message."

    email_system.send_email(sender, to_emails=["alice@example.com"], subject=subject, body=body)

    alice_inbox = email_system.get_emails("alice@example.com")
    charlie_inbox = email_system.get_emails("charlie@example.com")

    assert len(alice_inbox) == 1
    assert len(charlie_inbox) == 1

    assert f"From: {sender}" in alice_inbox[0]
