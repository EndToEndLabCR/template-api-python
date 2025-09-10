import pytest
from unittest.mock import patch

from src.app.config import AppConfiguration, DEFAULT_ENVIRONMENT
from src.app.config import Paths


@pytest.fixture
def reset_singleton():
    """
    Fixture to reset the Singleton instance of AppConfiguration before each test.
    """
    AppConfiguration._instance = None
    yield
    AppConfiguration._instance = None


@patch("app.configuration.app_config.load_dotenv")
@patch("os.environ.get")
def test_load_environment_variables(mock_get_env, mock_load_dotenv, reset_singleton):
    """
    Test loading environment variables from the .env file.
    """
    mock_load_dotenv.return_value = None  # Mock load_dotenv behavior
    mock_get_env.side_effect = lambda key, default=None: {
        "APP_ENV": "test"
    }.get(key, default)

    config = AppConfiguration.instance()
    assert config.env == "test"
    mock_load_dotenv.assert_called_once_with(Paths.ENV_FILE_PATH)


@patch("app.configuration.app_config.parse_config")
@patch("os.environ.get")
def test_fallback_to_default_environment(mock_get_env, mock_parse_config, reset_singleton):
    """
    Test fallback behavior when the APP_ENV variable is not set or invalid.
    """
    mock_get_env.return_value = None  # Simulate APP_ENV being None
    mock_parse_config.return_value = {}

    config = AppConfiguration.instance()
    assert config.env == DEFAULT_ENVIRONMENT


@patch("app.configuration.app_config.parse_config")
@patch("os.environ.get")
def test_load_config_test_yaml(mock_get_env, mock_parse_config, reset_singleton):
    """
    Test loading the 'config_test.yml' file for the 'test' environment.
    """
    mock_get_env.side_effect = lambda key, default=None: {
        "APP_ENV": "test"
    }.get(key, default)

    # Mock parse_config to simulate loading config_test.yml
    mock_parse_config.return_value = {
        "aws": {
            "access_id": "mock_access_id_123",
            "access_secret": "mock_access_secret_123"
        }
    }

    # Initialize the AppConfiguration instance
    config = AppConfiguration.instance()

    # Ensure the environment is set to 'test'
    assert config.env == "test"

    # Check that the AWS keys are loaded correctly
    assert config.config["app"]["name"] == "app_name"
    assert config.config["app"]["debug"] == "true"

    # Ensure parse_config was called with the correct file path
    expected_config_file = str(Paths.CONFIG_DIR / "config_test.yml")
    mock_parse_config.assert_called_once_with(path=expected_config_file)


@patch("app.configuration.app_config.load_dotenv")
@patch("os.environ.get")
def test_reset_singleton_instance(mock_get_env, mock_load_dotenv):
    """
    Test resetting the Singleton instance for testing purposes.
    """
    mock_load_dotenv.return_value = None
    mock_get_env.return_value = "test"

    # First instance
    config1 = AppConfiguration.instance()
    assert config1.env == "test"

    # Reset the Singleton instance
    AppConfiguration._instance = None

    # Create a new instance
    config2 = AppConfiguration.instance()
    assert id(config1) != id(config2)  # Ensure the instances are different
