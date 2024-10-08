
import os
from schema import Schema, And, Or, Use, Optional

from .constants import PREDEFINED_VARIABLES
from .util import parse_value

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
        sections = splitted_path[:-1]  # remove the key itself

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
                        print(f"Warning: Section {
                              section} not found in config file.")
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
                        print(f"Warning: Section {
                              section} not found in config file.")
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
                res = [str(res_item) + str(pres_item)
                       for res_item in res for pres_item in partial_res]
            # res is a list and partial_res is a string
            elif isinstance(partial_res, str) and isinstance(res, list):
                res = [str(item) + str(partial_res) for item in res]
            else:  # both strings
                res = res + partial_res
        else:
            print(f"Warning: Variable {
                  variable_name} not found in config file.")
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


def load_config(config_path, command_line_config):
    '''
    Loads a configuration from the specified file path.

    Args:
        config_path (str): The path to the configuration file.

    Returns:
        dict: The loaded configuration as a dictionary.
    '''
    config = command_line_config.copy()
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
                        subsections = [ss.strip()
                                       for ss in section.split("|", 1)[1].split("|")]
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
                        if section not in config:
                            config[section] = {}
                    continue
                else:
                    if '=' not in line:
                        print(f"Warning: invalid line ({
                              i_line+1}) ignored: {line}")
                        continue
                    # finally extract key-value pair
                    key, value = line.split('=', 1)
                    interpreted_value = parse_value(value.strip())
                    if len(subsections) > 0:
                        for ss in subsections:
                            if key.strip() not in config[section][ss]: # do not override command line config
                                config[section][ss][key.strip()] = _variable_replace_single(
                                    config, f'{section}.{ss}.{key.strip()}', interpreted_value)
                    else:
                        if key.strip() not in config[section]: # do not override command line config
                            config[section][key.strip()] = _variable_replace_single(
                                config, f'{section}.{key.strip()}', interpreted_value)
    else:
        print(f'Warning: file {config_path} does not exist')

    return config


######## VALIDATION ########

# Defining the schema
config_schema = Schema({
    # Main section schema
    'main': {
        'index_file': str,                       # index_file is required
        Optional('extensions'): Or(str, list),   # extensions is a list of string or a string
        Optional('iexts'): Or(str, list),        # ignores extensions is a list of string or a string
        Optional('meta'): Or(str, list)          # meta values is a list of string or a string
    },

    # Output section schema
    'output': {
        'dir': str,              # directory as string
        'type': Or(str, list)    # type is a list of string or a string
    },

    # Parser section schema
    'parser': {
        'begin_doc': str,                      # begin_doc is a string
        'end_doc': str,                        # end_doc is a string
        'doc_level': int,                      # doc_level is an int
        Optional('allow_sl_comments'): bool,   # boolean for single-line comments
        Optional('peek_lines'): int,           # peek_lines must be an integer
        # Dynamic keys (e.g., language-specific configs like 'parser|py')
        Optional(str): {
            'begin_ml_comment': str,               # multiline comment start as string
            'end_ml_comment': str,                 # multiline comment end as string
            Optional('allow_sl_comments'): bool,   # boolean for sl comments
            Optional('peek_lines'): int,           # peek_lines must be an integer
        }
    }
})

def validate_config(config):
    '''
    Validates the configuration against the defined schema.
    Args:
        config (dict): The configuration dictionary to validate.

    Returns:
        dict: The validated configuration dictionary.
    '''
    return config_schema.validate(config)
