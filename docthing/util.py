''' BEGIN FILE DOCUMENTATION
This comes from the docthing/util.py file.
END FILE DOCUMENTATION '''

import os
from .constants import PREDEFINED_VARIABLES

########## COMMON UTILS ##########

# Helper function to create output directory if it doesn't exist
def create_output_directory(output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)


########## CONFIGURATION FILE ##########

# Perform variable replacement in a string
def variable_replace_single(config, variable_path_in_config, value):
    if not isinstance(value, str):
        return value

    print()
    print(f"variable_path_in_config: {variable_path_in_config}")
    print(f"value: {value}")

    remaining_value = value
    res = ''
    # Check if the value contains any variables
    while '{' in remaining_value and '}' in remaining_value:
        handled = False
        res += remaining_value.split('{')[0]
        # Extract the variable name
        variable_name = remaining_value.split('{')[1].split('}')[0]
        # Check if the variable is predefined
        if variable_name in PREDEFINED_VARIABLES:
            res += PREDEFINED_VARIABLES[variable_name](config)
            handled = True

        if not handled:
            # Split the variable name into sections
            sections = variable_name.split('.')
            key = sections[-1]
            sections = sections[:-1]
            # Traverse the configuration dictionary
            current = config
            for section in sections:
                if section not in current:
                    print(f"Warning: Section {section} not found in {variable_path_in_config}.")
                    break
                current = current[section]

            if key in current:
                # Get the value for the last section
                current_value = current[key]
                # Replace the variable with the value
                res += str(current_value)
                handled = True
            else:
                print(f"Warning: Section {key} not found in {variable_path_in_config}.")


        if not handled:
            print(f"Warning: Variable {variable_name} not found in {variable_path_in_config}.")
            # reappend the variable name into the string
            res += '{' + variable_name + '}'

        remaining_value = remaining_value.split('}', 1)[0]
    return res

# Parse values from a string from config
def parse_value(value_str):
    if value_str.lower() == 'true':
        return True
    elif value_str.lower() == 'false':
        return False
    try:
        return int(value_str)
    except ValueError:
        try:
            return float(value_str)
        except ValueError:
            return value_str

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
                        # extract the subsections...
                        subsections = [ss.strip() for ss in section.split("|", 1)[1].split("|")]
                        # ... and the section
                        section = section.split("|", 1)[0]
                        # check main section was already initialized otherwise initialize it
                        if section not in config:
                            config[section] = {}
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
                        print(f"Warning: invalid line ({i_line+1}) ignored: {line}")
                        continue
                    # finally extract key-value pair
                    key, value = line.split('=', 1)
                    interpreted_value = parse_value(value.strip())
                    if len(subsections) > 0:
                        for ss in subsections:
                            config[section][ss][key.strip()] = variable_replace_single(config, f'{section}.{ss}.{key.strip()}', interpreted_value)
                    else:
                        config[section][key.strip()] = variable_replace_single(config, f'{section}.{key.strip()}', interpreted_value)
    return config

