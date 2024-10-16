# SPDX-License-Identifier: MIT
''' BEGIN FILE DOCUMENTATION (level: 3)
Other testing lines
TODO: extractor documentation
END FILE DOCUMENTATION '''


import re
import os
from .util import parse_value


# =======================
# PUBLIC
# =======================

def extract_documentation(path_to_file, parser_config):
    '''
    Extracts the documentation from the specified file path using the provided parser
    configuration.

        Args:
            path_to_file (str): The path to the file to extract documentation from.
            parser_config (dict): The parser configuration dictionary to use for
            extracting the documentation.

        Returns a tuple:
            first element is a str or None: The extracted documentation, or None if no
            documentation was found.
            second element is a dict or None: The extracted options, or None if no
            documentation was found.
    '''
    if path_to_file.endswith('.md'):
        with open(path_to_file, 'r') as f:
            return f.readlines(), {}

    res, options = _peek_n_read_if_match(path_to_file, parser_config)

    if res is None:
        print(
            'Warning: no documentation found correspondig to path ' +
            path_to_file)

    return res, options


# =======================
# REGULAR EXPRESSIONS
# =======================

def _regex_begin_documentation(parser_config):
    '''
    Generates a regular expression to match the end of a documentation block based
    on the provided parser configuration.

        Args:
            parser_config (dict): The parser configuration dictionary.

        Returns:
            A tuple of re.Pattern both matching the beginning of the documentation:
            the first is the one used to match multiline comments, the second is
            the one used to match single line comments.
            If `allow_sl_comments` is False, the second is None.
    '''
    sl_comment_regex = None
    if _does_allow_sl_comments(parser_config):
        res = '^' + parser_config['sl_comment'] + \
            ' *' + parser_config['begin_doc'] + ' *(\\(.*\\))? *$'
        sl_comment_regex = re.compile(res)

    res = '^' + parser_config['begin_ml_comment'] + \
        ' *' + parser_config['begin_doc'] + ' *(\\(.*\\))? *$'

    return re.compile(res), sl_comment_regex


def _regex_end_documentation(parser_config):
    '''
    Generates a regular expression to match the end of a documentation block based
    on the provided parser configuration.

        Args:
            parser_config (dict): The parser configuration dictionary.

        Returns:
            A tuple of re.Pattern both matching the ending of the documentation:
            the first is the one used to match multiline comments, the second is
            the one used to match single line comments.
            If `allow_sl_comments` is False, the second is None.
    '''
    sl_comment_regex = None
    if _does_allow_sl_comments(parser_config):
        res = '^' + parser_config['sl_comment'] + \
            ' *' + parser_config['end_doc'] + ' *$'
        sl_comment_regex = re.compile(res)

    res = '^ *' + parser_config['end_doc'] + ' *' + \
        parser_config['end_ml_comment'] + ' *$'
    return re.compile(res), sl_comment_regex


def _remove_sl_comment(line, parser_config):
    '''
    Removes the single-line comment from the given line using `sl_comment` if
    the `allow_sl_comments` option is enabled in the parser configuration.

    Please, note that exaxtly one space is matched after the `sl_comment`
    character(s).
    '''
    if not _does_allow_sl_comments(parser_config):
        return line

    return re.sub('^' + parser_config['sl_comment'] + ' ', '', line)


def _does_allow_sl_comments(parser_config):
    '''
    Checks if single-line comments are allowed in the current parser configuration.
    '''
    return 'allow_sl_comments' in parser_config and parser_config['allow_sl_comments']


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


def is_begin(line, regex_ml, regex_sl, is_sl):
    '''
    Checks if the given line matches the beginning of a documentation block based
    on the provided regular expressions and the current state of the documentation
    block.

        Args:
            line (str): The line to be checked.
            regex_ml (re.Pattern): The regular expression to match the begin of a
            multiline documentation block.
            regex_sl (re.Pattern): The regular expression to match the begin of a
            single-line documentation block.
            is_sl (bool): (input-output parameter) Whether the single-line regex
            should be used. If False, the multiline regex is used.
    '''
    # If the value of is_sl was already set this means the begin was already
    # found!
    if is_sl is not None:
        return False, is_sl

    ml_match = re.search(regex_ml, line)
    sl_match = re.search(regex_sl, line) if regex_sl else None

    # multiline takes precedence over single line
    if ml_match:
        is_sl = False
    elif sl_match:
        is_sl = True
    # NOTE: the `else` case is intentionally left out to let is_sl be None
    # if neither is found (setting it to none in the `else` case is wrong
    # since it would override the previous value)

    return ml_match or sl_match, is_sl


def is_end(line, regex_ml, regex_sl, is_sl):
    '''
    Checks if the given line matches the end of a documentation block based on
    the provided regular expressions and the current state of the documentation
    block.

        Args:
            line (str): The line to be checked.
            regex_ml (re.Pattern): The regular expression to match the end of a
            multiline documentation block.
            regex_sl (re.Pattern): The regular expression to match the end of a
            single-line documentation block.
            is_sl (bool): Whether the single-line regex should be used. If False,
            the multiline regex is used.
    '''
    # matches just one between ml and sl based on what is_begin found
    if is_sl is True:
        return re.search(regex_sl, line), is_sl
    elif is_sl is False:
        return re.search(regex_ml, line), is_sl
    return False, is_sl


# =======================
# IO
# =======================

def _peek_n_read_if_match(path_to_file, parser_config):
    '''
    Peeks the source code file to check for the presence of a documentation string
    and reads until the end of the documentation if found.

        Args:
            path_to_file (str): The path to the file to be processed.
            parser_config (dict): The parser configuration dictionary.

        Returns:
            (list[str], options) or None: A list of strings containing the lines of
            the documentation block and extracted options in a tuple, or None if no
            documentation block is found.
    '''
    ext = os.path.splitext(path_to_file)[1].replace('.', '')

    # generate a parser_config specific to the current file extension
    current_config = parser_config.copy()
    if ext in parser_config:
        for k, v in current_config[ext].items():
            current_config[k] = v

    begin_regex_ml, begin_regex_sl = _regex_begin_documentation(current_config)
    end_regex_ml, end_regex_sl = _regex_end_documentation(current_config)

    is_sl = None

    def _is_begin(line):
        nonlocal is_sl
        res, is_sl = is_begin(line, begin_regex_ml, begin_regex_sl, is_sl)
        return res

    def _is_end(line):
        nonlocal is_sl
        res, is_sl = is_end(line, end_regex_ml, end_regex_sl, is_sl)
        return res

    with open(path_to_file) as input_file:
        # Peek the first `line_number` lines
        document_lines = [next(input_file)
                          for _ in range(current_config['peek_lines'])]

        first_line_index = [i for i, line in enumerate(
            document_lines) if _is_begin(line)]

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
                document_lines.append(_remove_sl_comment(line, current_config))
                if _is_end(line):
                    break
                last_line_index += 1
            except StopIteration:
                print(
                    'Warning: reached end of file before end of documentation: ' +
                    'this usually means that the documentation is not properly ' +
                    'closed or the entire file contains only documentation')
                break

        return document_lines[first_line_index:last_line_index + 1], options
