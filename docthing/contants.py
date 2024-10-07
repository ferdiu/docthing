''' BEGIN FILE DOCUMENTATION
This comes from the docthing/constants.py file.
END FILE DOCUMENTATION '''

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