# SPDX-License-Identifier: MIT
import pytest
from unittest.mock import MagicMock, patch
from schema import Schema, SchemaError

from docthing.plugins.plugin_interface import PluginInterface


class MockPlugin(PluginInterface):
    """
    A mock implementation of PluginInterface for testing purposes.
    """

    def __init__(self):
        self.dependencies = ["python", "git"]
        self.configured = False

    def _enable(self):
        pass

    def _disable(self):
        pass

    def get_name(self):
        return "MockPlugin"

    def get_description(self):
        return "A mock plugin for testing purposes."

    def get_dependencies(self):
        return self.dependencies

    def schema(self):
        return Schema({"key": str})

    def _configure(self, _config: dict):
        self.configured = True


@pytest.fixture
def mock_documentation_blob():
    """
    Fixture to provide a mock DocumentationBlob instance.
    """
    return MagicMock()


@pytest.fixture
def mock_plugin(mock_documentation_blob):
    """
    Fixture to provide an instance of MockPlugin.
    """
    return MockPlugin()


def test_plugin_enable(mock_plugin):
    """
    Test the enable method of PluginInterface.
    """
    config = {"key": "value"}
    mock_plugin.enable(config=config)

    assert mock_plugin.is_enabled()
    assert mock_plugin.configured
    assert mock_plugin.enabled


def test_plugin_disable(mock_plugin):
    """
    Test the disable method of PluginInterface.
    """
    mock_plugin.enable(config={"key": "value"})
    assert mock_plugin.is_enabled()

    mock_plugin.disable()
    assert not mock_plugin.is_enabled()


def test_plugin_dependencies_available(mock_plugin):
    """
    Test the are_dependencies_available method.
    """
    with patch("shutil.which", return_value=True):
        assert mock_plugin.are_dependencies_available()

    with patch("shutil.which", side_effect=lambda x: x != "git"):
        assert not mock_plugin.are_dependencies_available()


def test_plugin_validate_config_success(mock_plugin):
    """
    Test configuration validation with a valid config.
    """
    config = {"key": "value"}
    validated = mock_plugin.validate(config)

    assert validated == config


def test_plugin_validate_config_failure(mock_plugin):
    """
    Test configuration validation with an invalid config.
    """
    config = {"key": 123}  # 'key' should be a string according to the schema
    with pytest.raises(SchemaError):
        mock_plugin.validate(config)


def test_plugin_configure(mock_plugin):
    """
    Test the configure method.
    """
    config = {"key": "value"}
    mock_plugin.configure(config)

    assert mock_plugin.configured


def test_plugin_invalid_configuration(mock_plugin):
    """
    Test configuring the plugin with an invalid configuration.
    """
    config = {"key": 123}  # 'key' should be a string according to the schema
    with pytest.raises(SchemaError):
        mock_plugin.configure(config)


def test_plugin_get_name(mock_plugin):
    """
    Test the get_name method.
    """
    assert mock_plugin.get_name() == "MockPlugin"


def test_plugin_get_description(mock_plugin):
    """
    Test the get_description method.
    """
    assert mock_plugin.get_description() == "A mock plugin for testing purposes."


def test_plugin_get_dependencies(mock_plugin):
    """
    Test the get_dependencies method.
    """
    assert mock_plugin.get_dependencies() == ["python", "git"]
