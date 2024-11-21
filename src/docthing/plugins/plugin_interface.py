# SPDX-License-Identifier: MIT
''' BEGIN FILE DOCUMENTATION (level: 2)
TODO: plugin_interface documentation
END FILE DOCUMENTATION '''

from abc import ABC, abstractmethod
import shutil
from schema import Schema


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
    def _enable(self) -> None:
        '''
        Enable the plugin and perform any necessary initialization.
        Overwrite this method in subclasses to implement plugin-specific
        initialization. Do not overwrite the `enable` (no underscore) method in subclasses.
        '''
        pass

    @abstractmethod
    def _disable(self) -> None:
        '''
        Disable the plugin and perform any necessary cleanup.
        Overwrite this method in subclasses to implement plugin-specific
        cleanup. Do not overwrite the `disable` (no underscore) method in subclasses.
        '''
        pass

    def enable(self, config: dict = {}) -> None:
        '''
        Enable the plugin and perform any necessary initialization.
        '''
        print(f'Enabling plugin: {self.get_name()}')
        self.configure(config)
        self._enable()
        self.enabled = True

    def disable(self) -> None:
        '''
        Disabling the plugin and perform any necessary cleanup.
        '''
        self._disable()
        self.enabled = False

    def is_enabled(self) -> bool:
        '''
        Check if the plugin is loaded.
        '''
        return self.enabled

    @abstractmethod
    def get_name(self) -> str:
        '''
        Return the name of the plugin.
        '''
        pass

    @abstractmethod
    def get_description(self) -> str:
        '''
        Return the description of the plugin.
        '''
        pass

    @abstractmethod
    def get_dependencies(self) -> list[str]:
        '''
        Return the list of dependencies required by the plugin.
        '''
        pass

    def are_dependencies_available(self) -> bool:
        '''
        Check if all the dependencies required by the plugin are available.
        '''
        for dep in self.get_dependencies():
            if not shutil.which(dep):
                return False
        return True

    def schema(self) -> Schema:
        '''
        Return the schema for the plugin configuration.
        Overwrite this method in subclasses to implement plugin-specific
        configuration schema used for validation.
        '''
        return Schema(dict)

    def validate(self, config: dict):
        '''
        Validate the provided configuration for the plugin.
        '''
        return self.schema().validate(config)

    def _configure(self, _config: dict) -> None:
        '''
        Configure the plugin with the provided configuration.
        Overwrite this method in subclasses to implement plugin-specific
        configuration. Do not overwrite the `configure` (no underscore) method in subclasses.
        '''
        pass

    def configure(self, config: dict) -> None:
        '''
        Configure the plugin with the provided configuration.
        '''
        validated_config = self.validate(config)
        if config == validated_config:
            self._configure(config)
        else:
            raise ValueError('invalid configuration for plugin ' +
                             self.get_name() + ': ' + str(config))
