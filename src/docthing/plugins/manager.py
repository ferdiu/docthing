

import os
import importlib.util
import inspect
import platform
from .plugin_interface import PluginInterface

SUPPORTED_PLUGIN_TYPES = ['exporter', 'meta-interpreter']


class PluginManager:
    def __init__(self, plugin_type, builtin_plugins=[]):
        '''
        Initialize the PluginManager with the specified plugin type.
        '''
        if platform.system() != 'Linux':
            raise Exception('PluginManager is only supported on Linux.')
        if plugin_type not in SUPPORTED_PLUGIN_TYPES:
            raise Exception('Plugin type not supported.')
        self.plugin_dir = os.environ.get(
            'HOME') + '/.local/share/docthing/plugins/' + plugin_type
        self.plugins = builtin_plugins

    def load_plugins(self, plugins='all'):
        '''
        Load all plugins from the specified directory.
        '''
        if plugins != 'all' and not isinstance(plugins, list):
            if isinstance(plugins, str):
                plugins = [plugins]
            else:
                raise Exception('Plugins must be a list of plugin names.')

        if os.path.isdir(self.plugin_dir):
            for filename in os.listdir(self.plugin_dir):
                if filename.endswith('.py'):
                    self._load_plugin_from_file(
                        os.path.join(self.plugin_dir, filename))

        if plugins == 'all':
            for plugin in self.plugins:
                plugin.load()
        else:
            available_plugins = [p.get_name() for p in self.plugins]
            unavailable_plugins = [
                p for p in plugins if p not in available_plugins]
            if len(unavailable_plugins) > 0:
                print(
                    f'Warning: some plugins were not found: {
                        ', '.join(unavailable_plugins)}')
            for plugin in self.plugins:
                if plugin.get_name() in plugins:
                    plugin.load()

    def unload_plugins(self):
        '''
        Unload all plugins.
        '''
        for plugin in self.plugins:
            plugin.unload()

    def _load_plugin_from_file(self, filepath):
        '''
        Load and verify a single plugin.
        '''
        module_name = os.path.splitext(os.path.basename(filepath))[0]

        # Load the module from file
        spec = importlib.util.spec_from_file_location(module_name, filepath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Inspect module for classes
        for name, obj in inspect.getmembers(module, inspect.isclass):
            # Check if the class is a subclass of PluginInterface and not the
            # abstract class itself
            if issubclass(obj, PluginInterface) and obj is not PluginInterface:
                print(f'Found plugin: {name}')
                self.plugins.append(obj())  # Instantiate the plugin class
