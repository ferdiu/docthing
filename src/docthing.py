''' BEGIN FILE DOCUMENTATION (level: 1)
This comes from the docthing.py file.
END FILE DOCUMENTATION '''

import os
import argparse
import json

from docthing.util import load_config, merge_configs, mkdir_silent
from docthing.constants import DEFAULT_CONFIG_FILE, DEFAULT_OUTPUT_DIR, DEFAULT_CONFIG
from docthing.index import process_index
from docthing.documentation_blob import DocumentationBlob
from docthing.plugins.manager import PluginManager
# from docthing.plugins.exporter. import TODO
from docthing.plugins.meta_interpreter.plantuml import PlantUMLInterpreter


# Main function to handle command-line arguments and execute the documentation generation
def main():
    parser = argparse.ArgumentParser(
        description="Generate documentation from project index file.")
    parser.add_argument(
        'index_file', help="Index file or project directory containing docthing.jsonc", nargs='?', default=os.getcwd())
    parser.add_argument(
        '--config', help="Relative to index directory path to configuration file", default=DEFAULT_CONFIG_FILE)
    parser.add_argument(
        '--outdir', help="Output directory for documentation", default=DEFAULT_OUTPUT_DIR)

    args = parser.parse_args()

    # Determine the index file
    if os.path.isdir(args.index_file):
        index_file = os.path.join(args.index_file, 'docthing.jsonc')
    else:
        index_file = args.index_file

    # Check if the index file exists
    if not os.path.exists(index_file):
        print(f"Error: Index file {index_file} does not exist.")
        return

    command_line_config = {
        'main': {
            'index': index_file
        },
        'output': {
            'dir': args.outdir
        }
    }

    # Load the configuration file
    config_path = args.config
    config = DEFAULT_CONFIG.copy()
    if os.path.isfile(config_path):
        config = merge_configs(config, load_config(config_path, command_line_config))

    # Determine the output directory and create it if needed
    output_dir = args.outdir
    mkdir_silent(output_dir)

    # Initialize the plugin manager for MetaInterpreters
    interpreter_manager = PluginManager(
        'meta-interpreter', [PlantUMLInterpreter])

    # Initialize the plugin manager for Exporters
    interpreter_manager = PluginManager('exporter', [])

    # Process the index file and generate the documentation
    # TODO: test from here
    process_index(index_file, output_dir, config)


if __name__ == "__main__":
    main()