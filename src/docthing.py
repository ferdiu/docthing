''' BEGIN FILE DOCUMENTATION (level: 1)
This comes from the docthing.py file.
END FILE DOCUMENTATION '''

import os
import argparse

from docthing.util import mkdir_silent
from docthing.config import load_config, merge_configs, validate_config
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
        '--outdir',
        help='Output directory for documentation',
        default=DEFAULT_OUTPUT_DIR)

    args = parser.parse_args()

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
        'meta-interpreter', [PlantUMLInterpreter({})])
    interpreter_manager.enable_plugins(
        config['main']['meta'] if 'meta' in config['main'] else [])

    # Initialize the plugin manager for Exporters
    exporter_manager = PluginManager(
        'exporter', [MarkdownExporter({})])
    exporter_manager.enable_plugins(config['output']['type'])

    # extract extensions and ignored extensions
    config['output']['extensions'] = config['output']['extensions'] if 'extensions' in config['output']['type'] else []
    config['output']['iexts'] = config['output']['iexts'] if 'iexts' in config['output']['type'] else []

    # Process the index file and generate the documentation
    blob = DocumentationBlob(
        index_file,
        config['parser'])

    # Apply all meta interpreters
    for interpreter in interpreter_manager.get_plugins():
        interpreter.interpret(blob)

    print(blob)

    # Output the documentation
    for exporter in exporter_manager.get_plugins():
        exporter.export(blob, config['output']['dir'])



if __name__ == '__main__':
    main()
