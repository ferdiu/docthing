
import re
import os
from .util import parse_value


# =======================
# PUBLIC
# =======================

def extract_documentation(path_to_file, parser_config):
    """
    Extracts the documentation from the specified file path using the provided parser
    configuration.

        Args:
            path_to_file (str): The path to the file to extract documentation from.
            parser_config (dict): The parser configuration dictionary to use for
            extracting the documentation.

        Returns:
            str or None: The extracted documentation, or None if no documentation
            was found.
    """
    res, options = _peek_n_read_if_match(path_to_file, parser_config)

    if res is None:
        print(
            'Warning: no documentation found correspondig to path ' +
            path_to_file)

    return res


# =======================
# REGULAR EXPRESSIONS
# =======================

def _regex_begin_documentation(ext, parser_config):
    '''
    Generates a regular expression to match the end of a documentation block based
    on the provided parser configuration.

        Args:
            ext (str): The file extension to use for the parser configuration.
            parser_config (dict): The parser configuration dictionary.

        Returns:
            re.Pattern: A compiled regular expression pattern that matches the end
            of a documentation block, or None if no parser configuration is found
            for the given extension.
    '''
    if ext not in parser_config:
        print('Warning: no parser configuration for extension ' + ext)
        return None

    if 'allow_sl_comments' in parser_config and parser_config['allow_sl_comments']:
        # TODO: implement support for single line comments
        raise ValueError('allow_sl_comments is not supported yet')
    else:
        res = '^' + parser_config[ext]['begin_ml_comment'] + \
            ' *' + parser_config['begin_doc'] + ' *(\\(.*\\))? *$'
        return re.compile(res)


def _regex_end_documentation(ext, parser_config):
    '''
    Generates a regular expression to match the end of a documentation block based
    on the provided parser configuration.

        Args:
            ext (str): The file extension to use for the parser configuration.
            parser_config (dict): The parser configuration dictionary.

        Returns:
            re.Pattern: A compiled regular expression pattern that matches the end
            of a documentation block, or None if no parser configuration is found
            for the given extension.
    '''
    if ext not in parser_config:
        print('Warning: no parser configuration for extension ' + ext)
        return None

    if 'allow_sl_comments' in parser_config and parser_config['allow_sl_comments']:
        # TODO: implement support for single line comments
        raise ValueError('allow_sl_comments is not supported yet')
    else:
        res = '^ *' + parser_config['end_doc'] + ' *' + \
            parser_config[ext]['end_ml_comment'] + ' *$'
        return re.compile(res)


# =======================
# OPTIONS
# =======================

def _parse_options(line):
    '''
    Parses the options string from a documentation block line.

    Args:
        line (str): The line containing the options string.

    Returns:
        dict: A dictionary of parsed options, where the keys are the option names and
        the values are the parsed option values.
    '''
    res = {}

    m = re.search(r'\((.*)\)', line)

    if not m:
        return res

    options = []
    if len(m.groups()) > 0 and m.groups()[0]:
        options = m.groups()[0].split(',')

    for opt in options:
        splitted = opt.split(':')
        if len(splitted) == 2:
            res[splitted[0].strip()] = parse_value(splitted[1].strip())
        else:
            res[splitted[0].strip()] = True

    return res


# =======================
# IO
# =======================

def _peek_n_read_if_match(path_to_file, parser_config):
    """
    Peeks the source code file to check for the presence of a documentation string
    and reads until the end of the documentation if found.

        Args:
            path_to_file (str): The path to the file to be processed.
            parser_config (dict): The parser configuration dictionary.

        Returns:
            (list[str], options) or None: A list of strings containing the lines of
            the documentation block and extracted options in a tuple, or None if no
            documentation block is found.
    """
    ext = os.path.splitext(path_to_file)[1].replace('.', '')
    begin_regex = _regex_begin_documentation(ext, parser_config)
    end_regex = _regex_end_documentation(ext, parser_config)

    with open(path_to_file) as input_file:
        # Peek the first `line_number` lines
        document_lines = [next(input_file)
                          for _ in range(parser_config['peek_lines'])]

        first_line_index = [i for i, item in enumerate(
            document_lines) if re.search(begin_regex, item)]

        # If none of the lines match the begin_regex, return None
        if len(first_line_index) == 0:
            return None, None

        first_line_index = first_line_index[0]

        options = _parse_options(document_lines[first_line_index])

        first_line_index += 1
        last_line_index = first_line_index

        # Read until the end of the documentation
        while True:
            try:
                line = next(input_file)
                document_lines.append(line)
                if re.search(end_regex, line):
                    break
                last_line_index += 1
            except StopIteration:
                print(
                    '''Warning: reached end of file before end of documentation:
                      this usually means that the documentation is not properly closed
                      or the entire file contains only documentation''')
                break

        return document_lines[first_line_index:last_line_index], options
