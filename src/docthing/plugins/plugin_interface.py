
from abc import ABC, abstractmethod
import shutil


class PluginInterface(ABC):
    '''
    Defines the interface for plugins in the docthing application.

    Plugins must implement the `load` and `unload` methods to handle plugin
    initialization and cleanup, respectively.
    '''

    def __init__(self, config):
        '''
        Initialize the plugin with the provided configuration.
        '''
        self.config = config
        self.loaded = False

    @abstractmethod
    def _load(self):
        '''
        Load the plugin and perform any necessary initialization.
        Overwrite this method in subclasses to implement plugin-specific
        initialization. Do not overwrite the `load` (no underscore) method in subclasses.
        '''
        pass

    @abstractmethod
    def _unload(self):
        '''
        Unload the plugin and perform any necessary cleanup.
        Overwrite this method in subclasses to implement plugin-specific
        cleanup. Do not overwrite the `unload` (no underscore) method in subclasses.
        '''
        pass

    def load(self):
        '''
        Load the plugin and perform any necessary initialization.
        '''
        print(f'Loading plugin: {self.get_name()}')
        self._load()
        self.loaded = True

    def unload(self):
        '''
        Unload the plugin and perform any necessary cleanup.
        '''
        self._unload()
        self.loaded = False

    def is_loaded(self):
        '''
        Check if the plugin is loaded.
        '''
        return self.loaded

    @abstractmethod
    def get_name(self):
        '''
        Return the name of the plugin.
        '''
        pass

    @abstractmethod
    def get_description(self):
        '''
        Return the description of the plugin.
        '''
        pass

    @abstractmethod
    def get_dependencies(self):
        '''
        Return the list of dependencies required by the plugin.
        '''
        pass

    def are_dependencies_available(self):
        '''
        Check if all the dependencies required by the plugin are available.
        '''
        for dep in self.get_dependencies():
            if not shutil.which(dep):
                return False
        return True
