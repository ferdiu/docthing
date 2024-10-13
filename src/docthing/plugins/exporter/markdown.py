
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
        complete_output = leaf.get_content()

        if isinstance(complete_output, list):
            complete_output = ''.join(complete_output)
        elif complete_output is None:
            complete_output = ''

        # If the page does not containe a title insert it
        for line in complete_output.split('\n'):
            if line.strip() != '':
                if not line.startswith('# '):
                    complete_output = '# ' + leaf.get_title() +\
                        '\n\n' + complete_output
                break

        with open(output_dir + '.md', 'w+') as f:
            f.write(complete_output)
