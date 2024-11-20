# SPDX-License-Identifier: MIT
''' BEGIN FILE DOCUMENTATION
The configuration file allows you to control various aspects of how docthing processes
your source code, including parsing rules, output formats, and file extensions to target.

## Table of Contents

- [Overview](#overview)
- [Predefined Variables](#predefined-variables)
- [Sections](#sections)
- [Variables](#variables)
- [Example](#example-configuration-file)

## Overview

By default the configuration file is assumed to be named `docthing.conf` and is located
in the same directory as the `index-file`.

The configuration file follows a standard format that supports the use of variables and
predefined values. Variables can be referenced using curly braces (`{}`), and sections
are denoted with square brackets (`[]`). Variables must be defined before being used in
the configuration file, and the file is divided into sections with specific purposes.
Some settings can be overridden via command-line options.

## Predefined Variables

- `index-file-dir`: Represents the directory where the index file is located. It is often
used in output paths to avoid hardcoding directory structures.

## Sections

### `[main]`

The `main` section includes general configurations, such as file extensions to process
and ignored files.

- `index_file`: Specifies the name of the index file. If this is also provided via the
command line, the command-line option takes precedence.
> Example:
> `index_file=docthing.jsonc`

- `meta`: Indicates the additional metadata to detect within the files. Markdown is always
detected, but you can specify others like plantuml for diagram inclusion.
> Example:
> `meta=plantuml`

### `[output]`

This section configures the output of the documentation process, such as the output
directory and format.

- `dir`: Specifies the directory where the documentation will be generated. You can use
predefined variables like {index-file-dir} to dynamically set the directory based on the
index file's location.
> Example:
> `dir={index-file-dir}/documentation`

- `type`: Specifies the formats in which documentation should be generated. Available
options include latex, html, markdown, and pdf. Please, note that the pdf generation
requires the LaTeX source to be generated.
> Example:
> `type=latex,html,markdown,pdf`

### `[parser]`

The parser section controls how docthing parses the source code for documentation. It
defines patterns to detect the start and end of documentation blocks, as well as some
additional options for controlling the parsing process.

- `begin_doc`: A string that defines what the parser should look for to detect the start
of a documentation block.
> Example:
> `begin_doc=BEGIN FILE DOCUMENTATION`

- `end_doc`: A string that defines what the parser should look for to detect the end of
a documentation block.
> Example:
> `end_doc=END FILE DOCUMENTATION`

- `doc_level`: Defines the maximum documentation level to extract. A level of 0 indicates
no limit. Refer to docthing's documentation for further details.
> Example:
> `doc_level=1`

- `exts`: Specifies the file extensions that docthing should process. If directories are
provided in the index file, this list will be used to find files to include in the
documentation. Multiple extensions can be provided, separated by commas.
> Example:
> `extensions=js,jsx,ts,tsx`

- `iexts`: Specifies file extensions to ignore when generating documentation. You can
reference previously declared variables here, such as {extensions}.
> Example:
> `iexts=test.{extensions}`

- `allow_sl_comments`: This boolean value specifies whether single-line comments are allowed
for documentation. By default, only multi-line comments are used.
> Example:
> `allow_sl_comments=false`

- `peek_lines`: Controls how many lines should be peeked ahead when searching for
documentation within a file. Setting this to 0 means all lines will be scanned, though this
is not recommended for performance reasons.
> Example:
> `peek_lines=1`

### `[parser|extsions-list]`

This section provides language-specific parser configurations for specific languages
source-code files. These settings can override general parser settings for these specific
file types.

- `begin_ml_comment`: Specifies the string used to mark the start of multi-line comments in all
files with extension(s) in `extensions-list`.
> Example:
> `begin_ml_comment=/*`

- `end_ml_comment`: Specifies the string used to mark the end of multi-line comments in all
files with extension(s) in `extensions-list`.
> Example:
> `end_ml_comment=*/`

- `sl_comment`: Specifies the string used to mark single-line comments in all
files with extension(s) in `extensions-list`.

## Variables

Variables are represented by names enclosed in curly braces (`{}`). They can be used to
replace specific values within the configuration. For instance, the variable `{index-file-dir}`
refers to the directory of the index file.

Variables can be referenced within the same section or across sections. When referencing
variables from the same section, only the variable name is required (e.g., `{var}`). To reference
variables from other sections, prefix them with the section name (e.g., `{section.var}`).

## Example Configuration File

```conf
[main]
index_file=docthing.jsonc
extensions=js,jsx,ts,tsx
iexts=test.{extensions}
meta=plantuml

[output]
dir={index-file-dir}/documentation
type=latex,html,markdown,pdf

[parser]
begin_doc=BEGIN FILE DOCUMENTATION
end_doc=END FILE DOCUMENTATION
doc_level=1
allow_sl_comments=false
peek_lines=1

[parser|js|jsx|ts|tsx]
begin_ml_comment=/*
end_ml_comment=*/
sl_comment=//
allow_sl_comments=false
```
### In this example:

The index file is `docthing.jsonc`.
Only `js`, `jsx`, `ts`, and `tsx` files will be processed.
Files with the pattern `test.{extensions}` will be ignored.
The output will be generated in a documentation folder inside the index file's directory.
Documentation will be output in LaTeX, HTML, Markdown, and PDF formats.
Parsing is customized for JavaScript and TypeScript files with multi-line comment support
and no single-line comments.

This configuration ensures `docthing` processes the right files, generates documentation in
multiple formats, and parses documentation blocks correctly.
END FILE DOCUMENTATION '''

import os
from schema import Schema, Or, Optional

from .constants import PREDEFINED_VARIABLES
from .util import parse_value


# =======================
# CONFIGURATION FILE
# =======================

def get_as_dot_config(config):
    '''
    Prints the configuration as a dot config file.
    '''
    res = ''
    for section, section_content_keys in config.items():
        res += f'[{section}]'
        res += '\n'

        if section == 'main' and 'index_file' not in section_content_keys:
            res += 'index_file='
            res += '\n'

        subsections = [
            k for k, v in section_content_keys.items() if isinstance(v, dict)]
        for key in section_content_keys.keys():
            if key in subsections:
                continue
            res += f'{key}={section_content_keys[key]}'
            res += '\n'
        res += '\n'

        for subsection in subsections:
            res += f'[{section}|{subsection}]'
            for key in section_content_keys[subsection].keys():
                res += f'{key}={section_content_keys[subsection][key]}'
                res += '\n'
            res += '\n'

    return res


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
        raise ValueError('Invalid scope type. Expected str or list.')

    if last_is_key:
        sections = sections[:-1]

    # Traverse the configuration dictionary
    current = config.copy()
    for section in sections:
        if section not in current:
            print(f'Warning: Section {section} not found in config file.')
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
        raise ValueError('Variables cannot be nested in the config file.')

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

        if inj_var_name in PREDEFINED_VARIABLES:
            # Injected variable name is a predefined variable
            partial_res = PREDEFINED_VARIABLES[inj_var_name](config)
            handled = True
        elif '.' in inj_var_name:
            # Injected variable name is an absolute path to a variable
            inj_var_scope = _go_into_scope(config, inj_var_sections)

            if inj_var_key in inj_var_scope:
                partial_res = inj_var_scope[inj_var_key]
                handled = True
            else:
                print(f'Warning: key {inj_var_key} not found ' +
                      f'in {".".join(inj_var_sections)}')
        else:
            # Injected variable name is in the same scope as the host variable
            host_var_scope = _go_into_scope(config, host_var_sections)

            if inj_var_key in host_var_scope:
                partial_res = host_var_scope[inj_var_key]
                handled = True
            else:
                print(f'Warning: key {inj_var_key} not found in ' +
                      f'{".".join(host_var_sections)} nor it is a predefined variable')

        # In the case of the source or the variable being a list
        #   it is necessary to convert the output to a list
        #   providing all possible combinations
        if handled:
            res = _combine_values(res, partial_res)
        else:
            print(
                f'Warning: Variable {inj_var_name} not found in config file.')
            # fallback to original string
            res = res + '{' + inj_var_name + '}'

        # Remove the part of the value that has been handled
        remaining_value = remaining_value.split('}', 1)[1]

    return _combine_values(res, remaining_value)


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


def _parse_section_tag(line):
    '''
    Parses a section tag from a line in a configuration file.

        Args:
            line (str): The line to parse.

        Returns:
            tuple: A tuple containing the section name and a list of subsections.
    '''
    section_name = line.strip().strip('[').strip(']').strip()

    if '|' not in section_name:
        return section_name, []
    else:
        section_name, remaining_line = section_name.split('|', 1)
        return section_name, remaining_line.split('|')


def _parse_key_value_pair(line):
    '''
    Parses a key-value pair from a line in a configuration file.

        Args:
            line (str): The line to parse.
        Returns:
            tuple: A tuple containing the key and value.
    '''
    return [p.strip() for p in line.split('=', 1)]


def _set_in_config(config, section, subsections, key, value, override=False):
    '''
    Sets a value in a configuration dictionary, creating nested dictionaries as needed.
    '''
    # No subsections
    if not subsections:
        if not override and key in config[section]:
            return

        config[section][key] = value
        config[section][key] = _variable_replace_single(
            config, f'{section}.{key}')
        return

    # Single subsection
    if isinstance(subsections, str):
        if not override and key in config[section][subsections]:
            return

        config[section][subsections][key] = value
        config[section][subsections][key] = _variable_replace_single(
            config, f'{section}.{subsections}.{key}')
        return

    # Multiple subsections
    for subsection in subsections:
        _set_in_config(config, section, subsection, key, value)


def load_config(config_path, command_line_config={}):
    '''
    Loads a configuration from the specified file path.

        Args:
            config_path (str): The path to the configuration file.
            command_line_config (dict): The command line configuration
            to merge with the loaded configuration.

        Returns:
            dict: The loaded configuration as a dictionary.
    '''

    config = command_line_config.copy()
    curr_section = 'main'
    curr_subsections = []

    if not os.path.exists(config_path):
        print(f'Warning: file {config_path} does not exist')
        return config

    with open(config_path, 'r') as f:
        lines = f.readlines()

    for i_line, line in enumerate(lines):
        line = line.strip()

        # Skip empty lines and comments
        if not line or line.startswith('#'):
            continue

        if line.strip().startswith('[') and line.strip().endswith(']'):
            # Found a section
            #   extract the section name and subsections
            curr_section, curr_subsections = _parse_section_tag(line)

            # Create section if not available
            if curr_section not in config:
                config[curr_section] = {}

            # Add subsections if not available
            for ss in curr_subsections:
                if ss not in config[curr_section]:
                    config[curr_section][ss] = {}
            continue

        if '=' in line:  # Found a key-value pair
            key, value = _parse_key_value_pair(line)

            _set_in_config(config, curr_section, curr_subsections,
                           key, parse_value(value))
            continue

        # Found line not part of the syntax
        print(f'Warning: invalid line ({i_line + 1}) ignored: {line}')
        continue

    return config


# =======================
# VALIDATION
# =======================

# Defining the schema
config_schema = Schema({
    # Main section schema
    'main': {
        'index_file': str,                       # index_file is required
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
        # extensions is a list of string or a string
        Optional('extensions'): Or(str, list),
        # ignores extensions is a list of string or a string
        Optional('iexts'): Or(str, list),
        # boolean for single-line comments
        Optional('allow_sl_comments'): bool,
        Optional('peek_lines'): int,           # peek_lines must be an integer
        # Dynamic keys (e.g., language-specific configs like 'parser|py')
        Optional(str): {
            'begin_ml_comment': str,               # multiline comment start as string
            'end_ml_comment': str,                 # multiline comment end as string
            'sl_comment': str,                     # single line comments
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
