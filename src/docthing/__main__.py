# SPDX-License-Identifier: MIT
''' BEGIN FILE DOCUMENTATION (level: 1)
This script is used to generate documentation for a project. It takes a
configuration file and an index file as input and generates a documentation
directory with the documentation.

## Command-line arguments

The script accepts the following command-line arguments:
- `index_file`: The path to the index file (this is the only positional argument).
- `-c`, `--config`: The path to the configuration file.
- `--config-dump`: Dump the default configuration file to stdout and exit.
- `-o`, `--outdir`: The path to the output directory.
- `-h`, `--help`: Show the help message and exit.

Alternatievly the `index_file` can be a directory containing a
`docthing.jsonc` file which will be used as `index_file`.

If no configuration file is provided, the default configuration file
`docthing.conf` will be looked up in the current directory. If found
it will be used otherwise the default configuration will be used instead.

If no `outdir` is specified, the default output directory `documentation`
will be used.
END FILE DOCUMENTATION '''

import os
import argparse

from docthing.plugins.meta_interpreter.nav import MarkdownNAVInterpreter
from docthing.util import mkdir_silent
from docthing.config import load_config, merge_configs, validate_config, get_as_dot_config
from docthing.constants import DEFAULT_CONFIG_FILE, DEFAULT_OUTPUT_DIR, DEFAULT_CONFIG
from docthing.documentation_blob import DocumentationBlob
from docthing.plugins.manager import PluginManager
from docthing.plugins.exporter.markdown import MarkdownExporter
from docthing.plugins.meta_interpreter.plantuml import PlantUMLInterpreter


# Main function to handle command-line arguments and execute the
# documentation generation
def main():
    parser = argparse.ArgumentParser(
        description='Generate documentation from project index file.')
    parser.add_argument(
        'index_file',
        help='Index file or project directory containing docthing.jsonc',
        nargs='?',
        default=os.getcwd())
    parser.add_argument(
        '--config',
        help='Relative to index directory path to configuration file',
        default=DEFAULT_CONFIG_FILE)
    parser.add_argument(
        '--config-dump',
        help='Dump the default configuration file to stdout and exit',
        action='store_true')
    parser.add_argument(
        '--outdir',
        help='Output directory for documentation',
        default=DEFAULT_OUTPUT_DIR)

    args = parser.parse_args()

    # Dump the default configuration file to stdout if requested
    if args.config_dump:
        print(get_as_dot_config(DEFAULT_CONFIG))
        return

    # Determine the index file
    if os.path.isdir(args.index_file):
        index_file = os.path.join(args.index_file, 'docthing.jsonc')
    else:
        index_file = args.index_file

    # Check if the index file exists
    if not os.path.exists(index_file):
        print(f'Error: Index file {index_file} does not exist.')
        return

    command_line_config = {
        'main': {
            'index_file': index_file
        },
        'output': {
            'dir': args.outdir
        }
    }

    # Load the configuration file
    config_path = args.config
    config = DEFAULT_CONFIG.copy()
    if os.path.isfile(config_path):
        config = merge_configs(
            config, load_config(
                config_path, command_line_config))

    validate_config(config)

    # Determine the output directory and create it if needed
    output_dir = args.outdir
    mkdir_silent(output_dir)

    # Initialize the plugin manager for MetaInterpreters
    interpreter_manager = PluginManager(
        'meta-interpreter', [PlantUMLInterpreter({}), MarkdownNAVInterpreter({})])
    interpreter_manager.enable_plugins(
        config['main']['meta'] if 'meta' in config['main'] else [])

    # Initialize the plugin manager for Exporters
    exporter_manager = PluginManager(
        'exporter', [MarkdownExporter({})])
    exporter_manager.enable_plugins(config['output']['type'])

    # Process the index file and generate the documentation
    blob = DocumentationBlob(
        index_file,
        config['parser'])

    # Print the documentation tree
    print('pre pruning')
    print(blob.to_string('|| '))

    # Prune the documentation blob based on the documentation level
    blob.prune_doc()

    # Print the documentation tree
    print('post pruning')
    print(blob.to_string('|| '))

    # Apply all meta interpreters
    for interpreter in interpreter_manager.get_plugins():
        interpreter.interpret(blob)

    # Print the documentation tree
    print('post interpreting')
    print(blob.to_string('|| '))

    # Output the documentation
    for exporter in exporter_manager.get_plugins():
        exporter.export(blob, config['output']['dir'])


if __name__ == '__main__':
    main()
