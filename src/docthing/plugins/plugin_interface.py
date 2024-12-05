# SPDX-License-Identifier: MIT
''' BEGIN FILE DOCUMENTATION (level: 2)
The strength of `docthing` is its extensibility. This feature is achieved
through the use of plugins.

A plugin is a Python module that implements the `PluginInterface` interface.
Plugins can be enabled and disabled using the `enable` and `disable` methods,
respectively. These two methods will call the `_enable` and `_disable` methods,
which are defined by the user implementing the `PluginInterface` interface.

### Definition

Every plugin should define a `name` attribute that is used to identify the plugin,
and a `description` attribute that describes the plugin and its `dependencies`.
This can be achieved by implementing the `get_name`, `get_description`, and
`get_dependencies` abstract methods. Dependencies are defined as a list of
strings that represent the names of the bianries expected to found in the system
that are required by the plugin to work properly. If the plugin has no dependencies,
the `get_dependencies` method should return an empty list.

### Tuning

Plugins can also support configuration through a configuration file. If so it should
define a `schema` method that returns a `Schema` object that is used to validate the
configuration. While enabling the plugin, the [`PluginManager`](@PluginManager) will
first `validate` the configuration using the provided `Schema` and then call the
`configure` method.
This method will call an `_configure` method that, in case the plugin needs additional
configuration, should be overwritten.

### Usage

It is up to the user to implement a method to actually _apply_ some changes to the
[`DocumentationBlob`](@DocumentationBlob) using the plugin. For instance, the
[`Exporter`](@Exporter) abstract class (and therefore all its subclasses) implements
the `export` method that takes a `DocumentationBlob` to export the documentation and
the [`MetaInterpreter`](@MetaInterpreter) implements the `interpret` method which
takes a `DocumentationBlob` to apply some changes to it, depending on the plugin
implementation.

### Create you plugin

To create a plugin, you need to create a new Python module that implements the
`PluginInterface` interface. The module should be placed in the `plugins`
directory of the docthing application. The module should define a class that
implements the `PluginInterface` interface directly if it is a Plugin of a _new type_
optherwise it should inherit from the appropriate abstract class (chosing between
[`MetaInterpreter`](@MetaInterpreter) and [`Exporter`](@Exporter), see related
documentation).
END FILE DOCUMENTATION '''

from abc import ABC, abstractmethod
import shutil
from schema import Schema
from typing import List


class PluginInterface(ABC):
    '''
    Defines the interface for plugins in the docthing application.

    Plugins must implement the `enable` and `disable` methods to handle plugin
    initialization and cleanup, respectively.
    '''

    def __init__(self):
        '''
        Initialize the plugin.
        '''
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
    def get_dependencies(self) -> List[str]:
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
