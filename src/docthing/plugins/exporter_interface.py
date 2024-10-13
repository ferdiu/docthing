
from abc import abstractmethod
import os

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
            print('Warning: Documentation is lazy. This means that no `meta` ' +\
                  'plugin was used on it before exporting.')
            documentation_blob.unlazy()

        plugin_out_dir = os.path.join(output_dir, self.get_name())

        mkdir_silent(output_dir)
        for leaf in documentation_blob.get_leaves():
            leaf_relative_path = os.path.join(*[p.get_title() for p in leaf.get_path()])
            leaf_complete_path = os.path.join(plugin_out_dir, leaf_relative_path)
            mkdir_silent(os.path.dirname(leaf_complete_path))
            self._export_leaf(leaf, leaf_complete_path)

    @abstractmethod
    def _export_leaf(self, leaf, output_file_no_ext):
        '''
        Exports a single leaf node to the specified format.
        The `output_file_no_ext` is the `path/to/file` without the extension.
        E.g. if the leaf is `path/to/file.md`, the `output_file_no_ext` is `path/to/file`.
        '''
        pass
