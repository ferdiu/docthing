''' BEGIN FILE DOCUMENTATION
This comes from the docthing/util.py file.
END FILE DOCUMENTATION '''

import os

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


