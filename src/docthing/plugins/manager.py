

import os
import importlib.util
import inspect
import platform
from .plugin_interface import PluginInterface

SUPPORTED_PLUGIN_TYPES = ['exporter', 'meta-interpreter']

class PluginManager:
    def __init__(self, plugin_type, builtin_plugins=[]):
        if platform.system() != 'Linux':
            raise Exception('PluginManager is only supported on Linux.')
        if not plugin_type in SUPPORTED_PLUGIN_TYPES:
            raise Exception('Plugin type not supported.')
        self.plugin_dir = os.environ.get('HOME') + '/.local/share/docthing/plugins/' + plugin_type
        self.plugins = builtin_plugins

    def load_plugins(self):
        '''Load all plugins from the specified directory.'''
        for filename in os.listdir(self.plugin_dir):
            if filename.endswith('.py'):  # Check for .py files
                self._load_plugin(os.path.join(self.plugin_dir, filename))

        for plugin in self.plugins:
            plugin.load()

    def _load_plugin(self, filepath):
        '''Load and verify a single plugin.'''
        module_name = os.path.splitext(os.path.basename(filepath))[0]

        # Load the module from file
        spec = importlib.util.spec_from_file_location(module_name, filepath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Inspect module for classes
        for name, obj in inspect.getmembers(module, inspect.isclass):
            # Check if the class is a subclass of PluginInterface and not the abstract class itself
            if issubclass(obj, PluginInterface) and obj is not PluginInterface:
                print(f'Found plugin: {name}')
                self.plugins.append(obj())  # Instantiate the plugin class
