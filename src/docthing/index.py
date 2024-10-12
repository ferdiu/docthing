''' BEGIN FILE DOCUMENTATION
This comes from the docthing/index.py file.
END FILE DOCUMENTATION '''

import os
import json
import shutil
from pathlib import Path
from .extractor import extract_documentation

from .util import mkdir_silent


# =======================
# PUBLIC
# =======================

# Function to process the index file and create the documentation
def process_index(index_file, output_dir, config):
    '''
    Processes the index file and creates the documentation for the project.

        Args:
            index_file (str): The path to the index file containing the project structure.
            output_dir (str): The path to the output directory where the documentation will be written.
            config (dict): A configuration dictionary containing the parser to use for extracting documentation.

        Returns:
            None
    '''
    with open(index_file, 'r') as f:
        index_data = json.load(f)

    # Handle the intro section if exists
    if 'intro' in index_data:
        intro_file = index_data['intro']
        _generate_documentation_from_source_code(
            intro_file, output_dir, 'intro.md', config)

    # Handle the quick start section if exists
    if 'quick' in index_data:
        quick_file = index_data['quick']
        _generate_documentation_from_source_code(
            quick_file, output_dir, 'quick_start.md', config)

    # Process the chapters and sections
    _process_chapters(
        index_data,
        output_dir,
        config,
        exclude_keys=[
            'intro',
            'quick'])


# =======================
# CHAPTER INTERPRETER
# =======================

def _process_chapters(data, output_dir, config, exclude_keys=[]):
    '''
    Recursively processes the chapters and sections in the index data, generating documentation for each item.

        Args:
            data (dict): The index data containing the chapters and sections.
            output_dir (str): The path to the output directory where the documentation will be written.
            config (dict): A configuration dictionary containing the parser to use for extracting documentation.
            exclude_keys (list, optional): A list of keys to exclude from processing. Defaults to an empty list.

        Returns:
            None
    '''
    for key, value in data.items():
        if key in exclude_keys:
            continue
        if key == '__index__':
            process_index(value, output_dir, exclude_keys, config)
        elif isinstance(value, str):
            # Single documentation file
            _generate_documentation_from_source_code(
                value, output_dir, key + '.md', config)
        elif isinstance(value, dict):
            # Nested documentation structure
            sub_dir = os.path.join(output_dir, key)
            mkdir_silent(sub_dir)
            _process_chapters(value, sub_dir, config)
        elif isinstance(value, list):
            # List of documentation files
            for i, filename in enumerate(value, start=1):
                _generate_documentation_from_source_code(
                    filename, output_dir, f'{key}_{i}.md', config)


# =======================
# FILE GENERATORS
# =======================

def _copy_file_to_output(src_file, output_dir, dest_filename):
    '''
    Copies a source file to the specified output directory with the given destination filename.

        Args:
            src_file (str): The path to the source file to be copied.
            output_dir (str): The path to the output directory where the file will be copied.
            dest_filename (str): The name of the file to be written in the output directory.

        Returns:
            None
    '''
    src_path = Path(src_file)
    if src_path.exists():
        shutil.copy(src_path, os.path.join(output_dir, dest_filename))
    else:
        print(f'Warning: {src_file} does not exist.')


def _generate_documentation_from_source_code(
        source_code, output_dir, dest_filename, config):
    '''
    Generates documentation for a source code file and writes it to the specified output directory.

        Args:
            source_code (str): The path to the source code file.
            output_dir (str): The path to the output directory where the documentation will be written.
            dest_filename (str): The name of the file to write the documentation to.
            config (dict): A configuration dictionary containing the parser to use for extracting documentation.

        Returns:
            None
    '''
    if source_code.endswith('.md'):
        return _copy_file_to_output(source_code, output_dir, dest_filename)

    doc = extract_documentation(source_code, config['parser'])

    if doc:
        with open(os.path.join(output_dir, dest_filename), 'w') as f:
            f.write(''.join(doc))
    else:
        # In no documentation was found, create an empty file
        with open(os.path.join(output_dir, dest_filename), 'w') as f:
            f.write('')
