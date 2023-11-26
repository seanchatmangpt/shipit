from utils.gherkin_parser import GherkinParser

# Sample Gherkin text for testing
SAMPLE_GHERKIN_TEXT = """
Feature: Test Matrix Factory
  Scenario Outline: Create a new project
    Given a project name "<project_name>"
    And the target directory "<target_directory>"
    And the repo url "<repo_url>"
    When I run the Matrix Factory with cookiecutter
    Then a new Flask project should be created

    Examples:
    | project_name    | target_directory          | repo_url                                         |
    | my_new_project  | /tmp/matrix_factory_output| https://github.com/cookiecutter-flask/cookiecutter-flask |
"""

def test_gherkin_parser_parses_feature_name():
    parser = GherkinParser(SAMPLE_GHERKIN_TEXT)
    feature = parser.parse()
    assert feature.name == "Test Matrix Factory"

def test_gherkin_parser_parses_scenarios():
    parser = GherkinParser(SAMPLE_GHERKIN_TEXT)
    feature = parser.parse()
    assert len(feature.scenarios) == 1
    assert feature.scenarios[0].name == "Create a new project"

def test_gherkin_parser_parses_scenario_steps():
    parser = GherkinParser(SAMPLE_GHERKIN_TEXT)
    feature = parser.parse()
    scenario = feature.scenarios[0]
    assert len(scenario.steps) > 0
    assert scenario.steps[0].step_type == "Given"
    assert "project name" in scenario.steps[0].description

# Additional tests can be added to cover more scenarios and edge cases
