# SPDX-License-Identifier: MIT
import pytest
from unittest.mock import MagicMock, patch
from schema import Schema

from docthing.plugins.manager import PluginManager
from docthing.plugins.plugin_interface import PluginInterface


class MockPlugin1(PluginInterface):
    """
    A mock implementation of PluginInterface for testing purposes.
    """

    def __init__(self):
        super().__init__()
        self.dependencies = ["python", "git"]
        self.configured = False

    def _enable(self):
        pass

    def _disable(self):
        pass

    def get_name(self):
        return "MockPlugin1"

    def get_description(self):
        return "A mock plugin for testing purposes."

    def get_dependencies(self):
        return self.dependencies

    def schema(self):
        return Schema({"key": dict})

    def _configure(self, _config: dict):
        self.configured = True


class MockPlugin2(PluginInterface):
    """
    A mock implementation of PluginInterface for testing purposes.
    """

    def __init__(self):
        super().__init__()
        self.dependencies = ["python", "git"]
        self.configured = False

    def _enable(self):
        pass

    def _disable(self):
        pass

    def get_name(self):
        return "MockPlugin2"

    def get_description(self):
        return "A mock plugin for testing purposes."

    def get_dependencies(self):
        return self.dependencies

    def schema(self):
        return Schema({"key": dict})

    def _configure(self, _config: dict):
        self.configured = True


@pytest.fixture
def mock_plugin_dir(tmp_path):
    """
    Fixture to create a mock plugin directory.
    """
    plugin_dir = tmp_path / "plugins"
    plugin_dir.mkdir()
    (plugin_dir / "plugin1.py").write_text("class Plugin1: pass")
    (plugin_dir / "plugin2.py").write_text("class Plugin2: pass")
    return str(plugin_dir)


@pytest.fixture
def mock_plugins():
    """
    Fixture to provide mock plugins.
    """
    return [
        MockPlugin1(),
        MockPlugin2(),
    ]


@patch("docthing.util.SUPPORTED_PLUGIN_TYPES", new=["mock_type"])
@patch("docthing.util.get_docthing_plugin_dir", new=mock_plugin_dir)
def test_plugin_manager_initialization(mock_plugins):
    """
    Test PluginManager initialization.
    """
    manager = PluginManager("mock_type", builtin_plugins=mock_plugins)
    assert len(manager.plugins) == 2
    assert manager.plugins[0].get_name() == "MockPlugin1"
    assert manager.plugins[1].get_name() == "MockPlugin2"


@patch("docthing.util.SUPPORTED_PLUGIN_TYPES", new=["mock_type"])
@patch("docthing.util.get_docthing_plugin_dir")
def test_enable_plugins_all(mock_get_dir, mock_plugins, tmp_path):
    """
    Test enabling all plugins.
    """
    mock_get_dir.return_value = str(tmp_path)
    manager = PluginManager("mock_type", builtin_plugins=mock_plugins)

    configs = {
        "MockPlugin1": {"key": {"setting": "value1"}},
        "MockPlugin2": {"key": {"setting": "value1"}}
    }
    manager.enable_plugins(plugins="all", configs=configs)

    assert all(plugin.enabled for plugin in mock_plugins)


@patch("docthing.util.SUPPORTED_PLUGIN_TYPES", new=["mock_type"])
@patch("docthing.util.get_docthing_plugin_dir")
def test_enable_specific_plugins(mock_get_dir, mock_plugins, tmp_path):
    """
    Test enabling specific plugins.
    """
    mock_get_dir.return_value = str(tmp_path)
    manager = PluginManager("mock_type", builtin_plugins=mock_plugins)

    configs = {
        "MockPlugin1": {"key": {"setting": "value1"}},
        "MockPlugin2": {"key": {"setting": "value1"}}
    }
    manager.enable_plugins(plugins=["MockPlugin1"], configs=configs)

    assert mock_plugins[0].enabled
    assert not mock_plugins[1].enabled


@patch("docthing.util.SUPPORTED_PLUGIN_TYPES", new=["mock_type"])
@patch("docthing.util.get_docthing_plugin_dir")
def test_disable_plugins(mock_get_dir, mock_plugins, tmp_path):
    """
    Test disabling all plugins.
    """
    mock_get_dir.return_value = str(tmp_path)
    manager = PluginManager("mock_type", builtin_plugins=mock_plugins)

    # Enable plugins first
    for plugin in manager.plugins:
        plugin.enable({"key": {"setting": "value1"}})

    # Disable plugins
    manager.disable_plugins()

    assert all(not plugin.enabled for plugin in mock_plugins)


@patch("docthing.util.SUPPORTED_PLUGIN_TYPES", new=["mock_type"])
@patch("os.listdir")
@patch("os.path.isdir")
def test_get_plugins_from_plugin_dir(mock_isdir, mock_listdir, tmp_path):
    """
    Test retrieving plugins from the plugin directory.
    """
    mock_isdir.return_value = True
    mock_listdir.return_value = [
        "plugin1.py", "plugin2.py", "not_a_plugin.txt"]

    manager = PluginManager("mock_type")
    plugins = manager._get_plugins_from_plugin_dir()

    assert "plugin1.py" in plugins
    assert "plugin2.py" in plugins
    assert "not_a_plugin.txt" not in plugins


@patch("docthing.util.SUPPORTED_PLUGIN_TYPES", new=["mock_type"])
@patch("importlib.util.spec_from_file_location")
@patch("importlib.util.module_from_spec")
def test_load_from_file(mock_module_from_spec, mock_spec_from_file_location):
    """
    Test loading a plugin from a file.
    """
    mock_spec = MagicMock()
    mock_spec_from_file_location.return_value = mock_spec

    mock_module = MagicMock()
    mock_module_from_spec.return_value = mock_module

    mock_module.Plugin1 = MockPlugin1

    manager = PluginManager("mock_type")
    manager._load_from_file("mock_path/plugin1.py")

    assert len(manager.plugins) == 1
    assert isinstance(manager.plugins[0], MockPlugin1)


@patch("docthing.util.SUPPORTED_PLUGIN_TYPES", new=["mock_type"])
def test_enable_plugins_invalid_type(mock_plugins):
    """
    Test enabling plugins with an invalid type.
    """
    manager = PluginManager("mock_type", builtin_plugins=mock_plugins)

    with pytest.raises(ValueError, match="Plugins must be a list of plugin names."):
        manager.enable_plugins(plugins=123)
