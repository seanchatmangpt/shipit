Scenario: Parsing and Interpreting an Email as a Task
    Given an incoming email to the UnixEmailSystem
    When the email is parsed
    Then the system should extract the sender, subject, and body
    And interpret the body to determine the required action
