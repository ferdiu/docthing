''' BEGIN FILE DOCUMENTATION
This comes from the docthing/constants.py file.
END FILE DOCUMENTATION '''

import os

# Constants for defaults
DEFAULT_CONFIG_FILE = 'docthing.conf'
DEFAULT_OUTPUT_DIR = 'documentation'
DEFAULT_CONFIG = {
    'main': {
        'meta': 'plantuml'
    },
    'output': {
        'dir': '{index-file-dir}/documentation',
        'type': 'markdown'
    },
    'parser': {
        'begin_doc': 'BEGIN FILE DOCUMENTATION',
        'end_doc': 'END FILE DOCUMENTATION',
        'doc_level': '1',
        'allow_sl_comments': False,
        'peek_lines': 1,
        # TODO: add default configuration options for most common languages here
    },
}

def index_file_dir(config):
    if not 'main' in config:
        print('using variable index-file-dir before defining \`main\` section in config file')
        return '{index-file-dir}'
    if not 'index_file' in config['main']:
        print('using variable index-file-dir before defining \`index_file\` in \`main\` section in config file')
        return '{index-file-dir}'
    return os.path.dirname(config['main']['index_file'])

PREDEFINED_VARIABLES = {
    'index-file-dir': lambda config: os.path.dirname(config['main']['index_file'])
}