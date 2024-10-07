''' BEGIN FILE DOCUMENTATION (level: 1)
This comes from the docthing.py file.
END FILE DOCUMENTATION '''

import os
import argparse

from .docthing.util import load_config, merge_configs, create_output_directory
from .docthing.contants import DEFAULT_CONFIG_FILE, DEFAULT_OUTPUT_DIR, DEFAULT_CONFIG
from .docthing.index import process_index


# Main function to handle command-line arguments and execute the documentation generation
def main():
    parser = argparse.ArgumentParser(description="Generate documentation from project index file.")
    parser.add_argument('index_file', help="Index file or project directory containing index.jsonc")
    parser.add_argument('--config', help="Relative to index directory path to configuration file", default=DEFAULT_CONFIG_FILE)
    parser.add_argument('--outdir', help="Output directory for documentation", default=DEFAULT_OUTPUT_DIR)

    args = parser.parse_args()

    # Determine the index file
    if os.path.isdir(args.index):
        index_file = os.path.join(args.index, 'index.jsonc')
    else:
        index_file = args.index

    # Check if the index file exists
    if not os.path.exists(index_file):
        print(f"Error: Index file {index_file} does not exist.")
        return

    # Load the configuration file
    config_path = args.config
    config = DEFAULT_CONFIG
    if os.path.isfile(config_path):
        config = merge_configs(config, load_config(config_path))

    print(config)

    # Determine the output directory and create it if needed
    output_dir = args.outdir
    create_output_directory(output_dir)

    # Process the index file and generate the documentation
    # TODO: test from here
    process_index(index_file, output_dir, config)


if __name__ == "__main__":
    main()
