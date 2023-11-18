import subprocess

import pytest
from typer.testing import CliRunner
from shipit.cli import app
from unittest.mock import patch
from shipit.shipit_project_config import ShipitProjectConfig

runner = CliRunner(mix_stderr=False)

@pytest.fixture
def mock_config(tmp_path):
    config = ShipitProjectConfig(
        project_name="Test Project",
        ship_date="2023-12-31",  # Added a default ship date
        directory=str(tmp_path)
    )
    config_file = tmp_path / 'shipit_project.yaml'
    config.save()
    return config_file

def test_render_command(mock_config):
    with patch('shipit.cli.ShipitProjectConfig.load', return_value=ShipitProjectConfig.load(mock_config)):
        result = runner.invoke(app, ["render"])
        print("Output:", result.stdout)
        print("Error:", result.stderr)
    assert result.exit_code == 0
    assert "Pages rendered successfully." in result.stdout

def test_build_command(mock_config):
    with patch('shipit.cli.subprocess.run') as mock_run:
        with patch('shipit.cli.ShipitProjectConfig.load', return_value=ShipitProjectConfig.load(mock_config)):
            result = runner.invoke(app, ["build"])
    assert result.exit_code == 0
    mock_run.assert_called_with(["mdbook", "build"], cwd=mock_config.parent)
    assert "mdbook built successfully." in result.stdout


def test_git_commit_success(mock_config):
    with patch('subprocess.run') as mock_run:
        result = runner.invoke(app, ["commit"], obj=mock_config)
        assert result.exit_code == 0
        mock_run.assert_called_once_with(["git", "add", "."], cwd=mock_config.directory)
        mock_run.assert_called_once_with(["git", "commit", "-m", "mock_commit_message"], cwd=mock_config.directory)

def test_git_commit_no_changes(mock_config):
    with patch('subprocess.run') as mock_run:
        # Simulate git status showing no changes
        mock_run.side_effect = [subprocess.CalledProcessError(1, "git")]
        result = runner.invoke(app, ["commit"], obj=mock_config)
        assert "No changes to commit" in result.stdout

def test_git_commit_failure(mock_config):
    with patch('subprocess.run') as mock_run:
        # Simulate git commit failure
        mock_run.side_effect = [None, subprocess.CalledProcessError(1, "git")]
        result = runner.invoke(app, ["commit"], obj=mock_config)
        assert result.exit_code != 0
        assert "Failed to commit changes" in result.stdout

def test_init_command(tmp_path):
    # Mock user input for the prompts in the init command
    user_inputs = [
        "Test Project",            # Project name
        "Test Description",        # Project description
        "2023-12-31",              # Ship date
        str(tmp_path)              # Directory
    ]

    with patch("typer.prompt", side_effect=user_inputs):
        result = runner.invoke(app, ["init"])

    # Check if the command executed successfully
    assert result.exit_code == 0

    # Verify that the configuration file is created
    config_file = tmp_path / 'shipit_project.yaml'
    assert config_file.exists()
