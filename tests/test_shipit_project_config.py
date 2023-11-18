import pytest
import yaml

from shipit.shipit_project_config import ShipitProjectConfig
from pathlib import Path
import tempfile

@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield tmpdirname

def test_save_and_load_config(temp_dir):
    config_path = Path(temp_dir) / "shipit_project.yaml"
    project_config = ShipitProjectConfig(
        project_name="Test Project",
        description="A test project",
        ship_date="2023-01-01",
        directory=str(temp_dir),
    )

    # Test saving the config
    project_config.save()
    assert config_path.exists()

    # Test loading the config
    loaded_config = ShipitProjectConfig.load(config_path)
    assert loaded_config.project_name == "Test Project"
    assert loaded_config.description == "A test project"
    assert loaded_config.ship_date == "2023-01-01"
    assert loaded_config.directory == str(temp_dir)

def test_update_config(temp_dir):
    project_config = ShipitProjectConfig(
        project_name="Initial Project",
        directory=str(temp_dir),
    )
    project_config.save()

    # Update the project name
    project_config.project_name = "Updated Project"
    project_config.save()

    # Load and check the updated project name
    loaded_config = ShipitProjectConfig.load(Path(temp_dir) / "shipit_project.yaml")
    assert loaded_config.project_name == "Updated Project"


def test_invalid_project_name(temp_dir):
    with pytest.raises(ValueError):
        ShipitProjectConfig(project_name=123, directory=str(temp_dir))  # Assuming project_name should be a string


def test_invalid_ship_date_format(temp_dir):
    with pytest.raises(ValueError):
        ShipitProjectConfig(project_name="Test", ship_date="Invalid-Date", directory=str(temp_dir))  # Assuming a specific date format


def test_load_from_nonexistent_file():
    with pytest.raises(FileNotFoundError):
        ShipitProjectConfig.load("nonexistent.yaml")


def test_load_from_invalid_format_file(temp_dir):
    config_path = Path(temp_dir) / "invalid_format.yaml"
    config_path.write_text("Not a YAML format")
    with pytest.raises(TypeError):
        ShipitProjectConfig.load(config_path)


def test_empty_project_name(temp_dir):
    with pytest.raises(ValueError):
        ShipitProjectConfig(project_name="", directory=str(temp_dir))

def test_long_project_name(temp_dir):
    long_name = "a" * 1000  # Assuming there is a length limit
    with pytest.raises(ValueError):
        ShipitProjectConfig(project_name=long_name, directory=str(temp_dir))
