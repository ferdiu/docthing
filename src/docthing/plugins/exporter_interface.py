# SPDX-License-Identifier: MIT
''' BEGIN FILE DOCUMENTATION (level: 2)
The `Exporter` interface is used to create plugins that export
documentation to a specific format.

> Even if you are interested in developing a meta-interpreter,
> I suggest you to read the documentation of [`Exporter`](@Exporter)
> plugins too to have a better understanding of how the whole
> process works.

## Implement an exporter

Exporters are really simple plugins to understand and, on the
theoretical level, they are really simple but their implementation
tends to be quite complicated.

The interface is quite simple and all you need to do is to implement
the following methods: `_export_leaf` and `import_function`.
The first one is used to export a single leaf node of the documentation
blob to the specified format and the second one is used to import an
external resoruce into the ouput documentation. For example see the
builtin `markdown` exporter: it implements different methods to create
different _imports_ for different types of resources: when the resource
is an image, it will replace the `ResourceReference` with the string
`![...](...)`. In an hypothetical LaTeX exporter, the import would
be something like `\\includegraphics{...}`.

The complexity is really behind this behaviour because the developer
should be able to define how to import a resource in any format.
The common syntax will always look like `@ref(type)-->[path]` as you
can see in the implementation of the method `__str__` in the
`ResourceReference` class.
END FILE DOCUMENTATION '''

from abc import abstractmethod
import os

from ..documentation_content import ResourceReference
from .plugin_interface import PluginInterface
from ..util import mkdir_silent


class Exporter(PluginInterface):
    '''
    Exporter is an abstract class that defines the interface for exporters.
    '''

    def export(self, documentation_blob, output_dir):
        '''
        Exports the documentation blob to the specified format.
        '''

        if documentation_blob.is_lazy():
            print(
                'Warning: Documentation is lazy. This means that no `meta` ' +
                'plugin was used on it before exporting.')
            documentation_blob.unlazy()

        plugin_out_dir = os.path.join(output_dir, self.get_name())

        mkdir_silent(output_dir)
        for leaf in documentation_blob.get_leaves():
            leaf_relative_path = os.path.join(
                *[p.get_title() for p in leaf.get_path()])
            leaf_complete_path = os.path.join(
                plugin_out_dir, leaf_relative_path)
            mkdir_silent(os.path.dirname(leaf_complete_path))
            self._export_leaf_resources(leaf, leaf_complete_path)
            leaf.replace_resources_with_imports(self.import_function)
            self._export_leaf(leaf, leaf_complete_path)

    @abstractmethod
    def _export_leaf(self, leaf, output_file_no_ext):
        '''
        Exports a single leaf node to the specified format.
        The `output_file_no_ext` is the `path/to/file` without the extension.
        E.g. if the leaf is `path/to/file.md`, the `output_file_no_ext` is `path/to/file`.
        '''
        pass

    @abstractmethod
    def import_function(self, leaf_title, resource):
        '''
        Returns the string to import an external resource in the output language.
        '''
        pass

    def _export_leaf_resources(self, leaf, output_file_no_ext):
        '''
        Exports the resources of a leaf node to the specified format.
        '''
        for resource in [line for line in leaf.get_content()
                         if isinstance(line, ResourceReference)]:
            resource.write(output_file_no_ext)
