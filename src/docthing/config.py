
import os
from schema import Schema, Or, Optional

from .constants import PREDEFINED_VARIABLES
from .util import parse_value


# =======================
# CONFIGURATION FILE
# =======================

def _combine_values(v1, v2):
    '''
    Helper function to combine two values.

    If they are both strings they will be concatenated.
    If one of them or both are lists then the combination will be returned as a list.
    '''
    res = v1

    # v1 is a list and res is a string
    if isinstance(v2, list) and isinstance(res, str):
        res = [res + str(item) for item in v2]
    # bot v1 and res are lists
    elif isinstance(v2, list) and isinstance(res, list):
        res = [str(v1_item) + str(v2_item)
               for v1_item in res for v2_item in v2]
    # res is a list and v1 is a string
    elif isinstance(v2, str) and isinstance(res, list):
        res = [str(item) + str(v2) for item in res]
    else:  # both strings
        res = res + v2

    return res


def _split_sections_key(sections_and_key):
    '''
    Helper function to split a key into sections and the last key.
    '''
    if isinstance(sections_and_key, str):
        sections_and_key = sections_and_key.split('.')

    return sections_and_key[:-1], sections_and_key[-1]


def _go_into_scope(config, path_in_dicts, last_is_key=False):
    '''
    Helper function to go into a scope in the configuration.
    '''
    # Split the scope into sections
    if isinstance(path_in_dicts, str):
        sections = path_in_dicts.split('.')
    elif isinstance(path_in_dicts, list):
        sections = path_in_dicts
    else:
        raise ValueError("Invalid scope type. Expected str or list.")

    if last_is_key:
        sections = sections[:-1]

    # Traverse the configuration dictionary
    current = config.copy()
    for section in sections:
        if section not in current:
            print(f"Warning: Section {section} not found in config file.")
            break
        current = current[section]
    return current


def _get_var_value(config, sections_and_key):
    '''
    Helper function to get the value of a variable in nested dictionaries.
    '''
    if isinstance(sections_and_key, str):
        sections_and_key = sections_and_key.split('.')

    sections, key = _split_sections_key(sections_and_key)

    return _go_into_scope(config, sections)[key]


def _variable_replace_single(config, host_var_path):
    '''
    Replaces a single variable in the provided configuration.

    This function takes a configuration dictionary and a variable path within the configuration.

    The function supports both simple variable names (e.g. `{my_variable}`) and nested variable
    names (e.g. `{section.my_variable}`). It also handles the case where the value is a list, and
    replaces each element of the list with the corresponding variable value.

    Args:
        config (dict): The configuration dictionary to use for variable replacement.
        host_var_path_in_config (str): The path to the variable within the configuration dictionary.

    Returns:
        str: The value with all variables replaced.
    '''
    host_var_value = _get_var_value(config, host_var_path)

    if isinstance(host_var_value, dict):
        raise ValueError("Variables cannot be nested in the config file.")

    if not isinstance(host_var_value, str) or '{' not in host_var_value:
        return host_var_value

    host_var_sections, _ = _split_sections_key(host_var_path)

    # Remaining value is the part of the value that has not been handled yet
    remaining_value = host_var_value
    res = ''

    # Check if the value contains any variables
    while '{' in remaining_value and '}' in remaining_value:
        handled = False
        res = res + remaining_value.split('{')[0]
        partial_res = ''

        # Extract the variable name
        inj_var_name = remaining_value.split('{')[1].split('}')[0]

        # Preserve key and sections
        inj_var_sections, inj_var_key = _split_sections_key(inj_var_name)

        print('INJECTED VARIABLE:', inj_var_name)
        print('PREDEFINED_VARIABLES', PREDEFINED_VARIABLES)

        if inj_var_name in PREDEFINED_VARIABLES:
            print('PREDEFINED')
            # Injected variable name is a predefined variable
            partial_res = PREDEFINED_VARIABLES[inj_var_name](config)
            handled = True
        elif '.' in inj_var_name:
            print('ABSOLUTE VARIABLE')
            # Injected variable name is an absolute path to a variable
            inj_var_scope = _go_into_scope(config, inj_var_sections)

            if inj_var_key in inj_var_scope:
                partial_res = inj_var_scope[inj_var_key]
                handled = True
            else:
                print(f"Warning: key {inj_var_key} not found in {
                      '.'.join(inj_var_sections)}")
        else:
            print('CURRENT SCOPE VARIABLE', host_var_sections)
            # Injected variable name is in the same scope as the host variable
            host_var_scope = _go_into_scope(config, host_var_sections)

            if inj_var_key in host_var_scope:
                partial_res = host_var_scope[inj_var_key]
                handled = True
            else:
                print(f"Warning: key {inj_var_key} not found in {
                      '.'.join(host_var_sections)} nor it is a predefined variable")

        print()

        # In the case of the source or the variable being a list
        #   it is necessary to convert the output to a list
        #   providing all possible combinations
        if handled:
            res = _combine_values(res, partial_res)
        else:
            print(
                f"Warning: Variable {inj_var_name} not found in config file.")
            # fallback to original string
            res = res + '{' + inj_var_name + '}'

        # Remove the part of the value that has been handled
        remaining_value = remaining_value.split('}', 1)[1]

    return res + remaining_value


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
                        subsections = [
                            ss.strip() for ss in section.split(
                                "|", 1)[1].split("|")]
                        # ... and the section
                        section = section.split("|", 1)[0]
                        # check main section was already initialized otherwise
                        # initialize it
                        if section not in config:
                            config[section] = {}
                        # initialize them empty
                        for ss in subsections:
                            if ss not in config[section]:
                                config[section][ss] = {}
                    else:
                        # if it was a normal section reset subesction and
                        # initialize it
                        subsections = []
                        if section not in config:
                            config[section] = {}
                    continue
                else:
                    if '=' not in line:
                        print(f"Warning: invalid line ({
                              i_line + 1}) ignored: {line}")
                        continue
                    # finally extract key-value pair
                    key, value = line.split('=', 1)
                    if len(subsections) > 0:
                        for ss in subsections:
                            if key.strip() not in config[section][ss]:
                                # do not override command line config
                                config[section][ss][key.strip()] = parse_value(
                                    value.strip())
                                config[section][ss][key.strip()] = _variable_replace_single(
                                    config, f'{section}.{ss}.{key.strip()}')
                    else:
                        if key.strip(
                        ) not in config[section]:
                            # do not override command line config
                            config[section][key.strip()] = parse_value(
                                value.strip())
                            config[section][key.strip()] = _variable_replace_single(
                                config, f'{section}.{key.strip()}')
    else:
        print(f'Warning: file {config_path} does not exist')

    return config


# =======================
# VALIDATION
# =======================

# Defining the schema
config_schema = Schema({
    # Main section schema
    'main': {
        'index_file': str,                       # index_file is required
        # extensions is a list of string or a string
        Optional('extensions'): Or(str, list),
        # ignores extensions is a list of string or a string
        Optional('iexts'): Or(str, list),
        # meta values is a list of string or a string
        Optional('meta'): Or(str, list)
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
        # boolean for single-line comments
        Optional('allow_sl_comments'): bool,
        Optional('peek_lines'): int,           # peek_lines must be an integer
        # Dynamic keys (e.g., language-specific configs like 'parser|py')
        Optional(str): {
            'begin_ml_comment': str,               # multiline comment start as string
            'end_ml_comment': str,                 # multiline comment end as string
            Optional('allow_sl_comments'): bool,   # boolean for sl comments
            # peek_lines must be an integer
            Optional('peek_lines'): int,
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
