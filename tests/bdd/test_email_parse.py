from pytest_bdd import given, when, then, parsers, scenarios

scenarios("../email-parsing-and-interpretation.feature")


@given("an incoming email to the UnixEmailSystem")
def given_incoming_email():
    # Implement your setup code here
    pass


@when("the email is parsed")
def when_email_is_parsed():
    # Implement the code to parse the email
    pass


@when("interpret the body to determine the required action")
def when_interpret_body_to_determine_action():
    # Implement code to interpret the body and determine the action
    pass


@then(parsers.parse("the system should extract the {sender}, {subject}, and {body}"))
def step_impl(sender, subject, body):
    raise NotImplementedError(
        "STEP: Then the system should extract the <sender>, <subject>, and <body>"
    )
