Feature: Email Parsing and Interpretation

  Scenario Outline: Parsing and Interpreting an Email
    Given an incoming email to the UnixEmailSystem
    When the email is parsed
    Then the system should extract the <sender>, <subject>, and <body>
    And interpret the body to determine the required action

    Examples:
      | sender             | subject           | body                                   |
      | "user@example.com" | "Task Assignment" | "Please review the attached report..." |
