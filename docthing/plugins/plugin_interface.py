
from abc import ABC, abstractmethod


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
