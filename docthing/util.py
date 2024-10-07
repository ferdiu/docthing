''' BEGIN FILE DOCUMENTATION
This comes from the docthing/util.py file.
END FILE DOCUMENTATION '''

import os

# Helper function to create output directory if it doesn't exist
def create_output_directory(output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

# Helper function to merge configurations
def merge_configs(config1, config2):
    merged_config = {}
    for key, value in config1.items():
        if key in config2:
            if isinstance(value, dict) and isinstance(config2[key], dict):
                merged_config[key] = merge_configs(value, config2[key])
            else:
                merged_config[key] = config2[key]
        else:
            merged_config[key] = value
    return merged_config

# Helper function to load the config file
def load_config(config_path):
    config = {}
    section = None
    subsections = []
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            lines = f.readlines()
            for i_line, line in enumerate(lines):
                line = line.strip()
                if not line or line.startswith("#"):
                    # Skip empty lines and comments
                    continue
                if line.startswith("[") and line.endswith("]"):
                    # Handle sections
                    section = line.strip("[]").strip()
                    if len(section.split("|", 1)) == 2:
                        # section with subsections
                        # check main section was already initialized otherwise initialize it
                        if section not in config:
                            config[section] = {}
                        # extract the subsections...
                        section = section.split("|", 1)[0]
                        # and the section
                        subsections = [ss.strip() for ss in section.split("|", 1)[1].split("|")]
                        # initialize them empty
                        for ss in subsections:
                            if ss not in config[section]:
                                config[section][ss] = {}
                    else:
                        # if it was a normal section reset subesction and initialize it
                        subsections = []
                        config[section] = {}
                    continue
                else:
                    if '=' not in line:
                        print(f"warning: invalid line ({i_line+1}) ignored: {line}")
                        continue
                    # finally extract key-value pair
                    key, value = line.split('=', 1)
                    if len(subsections) > 0:
                        for ss in subsections:
                            config[section][ss] = value.strip()
                    else:
                        config[section][key.strip()] = value.strip()
    return config

