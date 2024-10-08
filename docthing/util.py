''' BEGIN FILE DOCUMENTATION
This comes from the docthing/util.py file.
END FILE DOCUMENTATION '''

import os
from .constants import PREDEFINED_VARIABLES

########## COMMON UTILS ##########

def mkdir_silent(output_dir):
    '''
    Creates the specified output directory if it doesn't already exist.

    This function checks if the given `output_dir` path exists, and if not, it creates the directory and any necessary parent directories using `os.makedirs()`.

    This is a utility function that can be used to ensure that an output directory is available before writing files to it.

    Args:
        output_dir (str): The path of the output directory to create.
    '''
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)


def parse_value(value_str):
    '''
    Parses a string value into a Python data type.

    This function takes a string representation of a value and attempts to convert it
    to the appropriate Python data type. It handles the following cases:

    - 'true' -> True
    - 'false' -> False
    - 'null' or 'none' -> None
    - Comma-separated list of values -> List of parsed values
    - Integer -> int
    - Float -> float
    - Otherwise, returns the original string

    This function is useful for parsing configuration values or other user-provided
    string data into the appropriate Python types.
    '''
    if value_str.lower() == 'true':
        return True
    elif value_str.lower() == 'false':
        return False
    elif value_str.lower() == 'null' or value_str.lower() == 'none':
        return None
    elif ',' in value_str:
        return [parse_value(item.strip()) for item in value_str.split(',')]
    try:
        return int(value_str)
    except ValueError:
        try:
            return float(value_str)
        except ValueError:
            return value_str


########## CONFIGURATION FILE ##########

def _variable_replace_single(config, variable_path_in_config, value):
    '''
    Replaces a single variable in the provided configuration with the given value.

    This function takes a configuration dictionary, a variable path within the configuration, and a value to replace the variable with. It handles the case where the value contains variables that need to be recursively replaced.

    The function first checks if the value contains any variables by looking for the `{` and `}` characters. If not, it simply returns the value as is.

    If the value does contain variables, the function extracts the variable name, looks up the value in the configuration, and replaces the variable with the corresponding value. If the variable is not found in the configuration, a warning is printed and the original variable name is left in the string.

    The function supports both simple variable names (e.g. `{my_variable}`) and nested variable names (e.g. `{section.my_variable}`). It also handles the case where the value is a list, and replaces each element of the list with the corresponding variable value.

    Args:
        config (dict): The configuration dictionary to use for variable replacement.
        variable_path_in_config (str): The path to the variable within the configuration dictionary.
        value (str): The value to replace the variable with.

    Returns:
        str: The value with all variables replaced.
    '''
    if not isinstance(value, str) or '{' not in value:
        return value

    remaining_value = value
    res = ''

    # Check if the value contains any variables
    while '{' in remaining_value and '}' in remaining_value:
        handled = False
        res = res + remaining_value.split('{')[0]
        partial_res = ''

        # Extract the variable name
        variable_name = remaining_value.split('{')[1].split('}')[0]

        splitted_path = variable_name.split('.')
        # Preserve key and sections
        sections = splitted_path[:-1] # remove the key itself

        # Check if the variable is predefined
        if variable_name in PREDEFINED_VARIABLES:
            partial_res = PREDEFINED_VARIABLES[variable_name](config)
            handled = True

        if not handled:
            if '.' in variable_name:
                # Traverse the configuration dictionary
                current = config.copy()
                for section in sections:
                    if section not in current:
                        print(f"Warning: Section {section} not found in config file.")
                        break
                    current = current[section]

                if variable_name in current:
                    # Get the value for the last section
                    current_value = current[variable_name]
                    # Replace the variable with the value
                    partial_res = current_value
                    handled = True
            else:
                # Traverse the configuration dictionary
                current_variable_scope = config.copy()
                for section in variable_path_in_config.split('.')[:-1]:
                    if section not in current_variable_scope:
                        print(f"Warning: Section {section} not found in config file.")
                        break
                    current_variable_scope = current_variable_scope[section]
                if variable_name in current_variable_scope:
                    partial_res = current_variable_scope[variable_name]
                    handled = True

        if handled:
            # partial_res is a list and res is a string
            if isinstance(partial_res, list) and isinstance(res, str):
                res = [res + str(item) for item in partial_res]
            # bot partial_res and res are lists
            elif isinstance(partial_res, list) and isinstance(res, list):
                res = [str(res_item) + str(pres_item) for res_item in res for pres_item in partial_res]
            # res is a list and partial_res is a string
            elif isinstance(partial_res, str) and isinstance(res, list):
                res = [str(item) + str(partial_res) for item in res]
            else: # both strings
                res = res + partial_res
        else:
            print(f"Warning: Variable {variable_name} not found in config file.")
            # reappend the variable name into the string
            res = res + '{' + variable_name + '}'

        remaining_value = remaining_value.split('}', 1)[0]
    return res


def merge_configs(config1, config2):
    '''
    Merges two configuration dictionaries, recursively handling nested dictionaries.

    Args:
        config1 (dict): The first configuration dictionary to merge.
        config2 (dict): The second configuration dictionary to merge.

    Returns:
        dict: A new dictionary that is the result of merging the two input configurations.
    '''
    merged_config = config1.copy()
    for key, value in config2.items():
        if key in config1:
            if isinstance(value, dict) and isinstance(config1[key], dict):
                merged_config[key] = merge_configs(config1[key], value)
            else:
                merged_config[key] = config2[key]
        else:
            merged_config[key] = value
    return merged_config


def load_config(config_path):
    '''
    Loads a configuration from the specified file path.

    Args:
        config_path (str): The path to the configuration file.

    Returns:
        dict: The loaded configuration as a dictionary.
    '''
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
                            config[section][ss][key.strip()] = _variable_replace_single(config, f'{section}.{ss}.{key.strip()}', interpreted_value)
                    else:
                        config[section][key.strip()] = _variable_replace_single(config, f'{section}.{key.strip()}', interpreted_value)
    else:
        print(f'Warning: file {config_path} does not exist')

    return config

