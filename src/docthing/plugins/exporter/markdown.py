# SPDX-License-Identifier: MIT

import os
from urllib.parse import quote

from ...documentation_content import ResourceReference
from ..exporter_interface import Exporter


class MarkdownExporter(Exporter):
    '''
    An exporter that exports documentation to Markdown format.
    '''

    def __init__(self, documentation_blob):
        '''
        Initializes the MarkdownExporter instance with the provided DocumentationBlob instance.
        '''
        super().__init__(documentation_blob)

    def _enable(self):
        pass

    def _disable(self):
        pass

    def get_name(self):
        return 'markdown'

    def get_description(self):
        return 'Export documentation to Markdown format.'

    def get_dependencies(self):
        return []

    def _export_leaf(self, leaf, output_dir):
        '''
        Exports a single leaf node to markdown format.
        '''
        output = leaf.get_content()

        if output is None:
            output = ''
        else:
            output = ''.join(output.get_printable())

        # If the page does not start with a title insert it
        for line in output.split('\n'):
            if not isinstance(line, str) and line.strip() != '':
                if not line.startswith('# '):
                    output = '# ' + leaf.get_title() +\
                        '\n\n' + output
                break

        with open(output_dir + '.md', 'w+') as f:
            f.write(output)

    def _link_import(self, leaf_title, resource_path):
        return f'[{leaf_title}](' +\
            quote(os.path.join(".", leaf_title + resource_path)) + ')\n'

    def _img_import(self, leaf_title, resource_path):
        return '!' + self._link_import(leaf_title, resource_path)

    def _import_file_import(self, resource_path):
        label = os.path.split(resource_path)[-1]
        if label.endswith('.md'):
            label = label[:-3]
        return f'<a href="{resource_path}">{label}</a>\n'

    def import_function(self, leaf_title, resource):
        if isinstance(resource, ResourceReference):
            if resource.get_type() == 'image':
                return self._img_import(leaf_title, resource.get_path())
            elif resource.get_type() in ['file', 'link']:
                return self._link_import(leaf_title, resource.get_path())
            elif resource.get_type() == 'import-file':
                return self._import_file_import(resource.get_path())
        elif isinstance(resource, str):
            type, path = ResourceReference.search(resource)
            if type == 'image':
                return self._img_import(leaf_title, path)
            elif type in ['file', 'link']:
                return self._link_import(leaf_title, resource.get_path())
            elif resource.get_type() == 'import-file':
                return self._import_file_import(resource)

        return '<p style="color: red">Unable to determine resource type (' +\
            str(resource) + ')</p>'
