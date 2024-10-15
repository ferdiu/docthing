# SPDX-License-Identifier: MIT
''' BEGIN FILE DOCUMENTATION (level: 2)
TODO: plugin_interface documentation
END FILE DOCUMENTATION '''

from abc import ABC, abstractmethod
import shutil


class PluginInterface(ABC):
    '''
    Defines the interface for plugins in the docthing application.

    Plugins must implement the `enable` and `disable` methods to handle plugin
    initialization and cleanup, respectively.
    '''

    def __init__(self, documentation_blob):
        '''
        Initialize the plugin with the provided DocumentationBlob instance.
        '''
        self.documentation_blob = documentation_blob
        self.enabled = False

    @abstractmethod
    def _enable(self):
        '''
        Enable the plugin and perform any necessary initialization.
        Overwrite this method in subclasses to implement plugin-specific
        initialization. Do not overwrite the `enable` (no underscore) method in subclasses.
        '''
        pass

    @abstractmethod
    def _disable(self):
        '''
        Disable the plugin and perform any necessary cleanup.
        Overwrite this method in subclasses to implement plugin-specific
        cleanup. Do not overwrite the `disable` (no underscore) method in subclasses.
        '''
        pass

    def enable(self):
        '''
        Enable the plugin and perform any necessary initialization.
        '''
        print(f'Enabling plugin: {self.get_name()}')
        self._enable()
        self.enabled = True

    def disable(self):
        '''
        Disabling the plugin and perform any necessary cleanup.
        '''
        self._disable()
        self.enabled = False

    def is_enabled(self):
        '''
        Check if the plugin is loaded.
        '''
        return self.enabled

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
