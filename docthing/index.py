''' BEGIN FILE DOCUMENTATION
This comes from the docthing/index.py file.
END FILE DOCUMENTATION '''

import os
import json
import shutil
from pathlib import Path

from .util import create_output_directory

# Function to process the index file and create the documentation
def process_index(index_file, output_dir, config):
    with open(index_file, 'r') as f:
        index_data = json.load(f)

    # Handle the intro section if exists
    if 'intro' in index_data:
        intro_file = index_data['intro']
        copy_file_to_output(intro_file, output_dir, 'intro.md')

    # Handle the quick start section if exists
    if 'quick' in index_data:
        quick_file = index_data['quick']
        copy_file_to_output(quick_file, output_dir, 'quick_start.md')

    # Process the chapters and sections
    process_chapters(index_data, output_dir)

# Recursive function to process chapters and documentation pieces
def process_chapters(data, output_dir):
    for key, value in data.items():
        if isinstance(value, str):
            # Single documentation file
            copy_file_to_output(value, output_dir, key + '.md')
        elif isinstance(value, dict):
            # Nested documentation structure
            sub_dir = os.path.join(output_dir, key)
            create_output_directory(sub_dir)
            process_chapters(value, sub_dir)
        elif isinstance(value, list):
            # List of documentation files
            for i, filename in enumerate(value, start=1):
                copy_file_to_output(filename, output_dir, f"{key}_{i}.md")

# Helper function to copy documentation files to the output directory
def copy_file_to_output(src_file, output_dir, dest_filename):
    src_path = Path(src_file)
    if src_path.exists():
        shutil.copy(src_path, os.path.join(output_dir, dest_filename))
    else:
        print(f"Warning: {src_file} does not exist.")