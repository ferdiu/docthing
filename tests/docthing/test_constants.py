# SPDX-License-Identifier: MIT

from unittest.mock import patch
from docthing.constants import DEFAULT_CONFIG, PREDEFINED_VARIABLES, index_file_dir, _c_like_languages_parser_config

# Test the constant for C-like language parser configuration


def test_c_like_languages_parser_config():
    assert _c_like_languages_parser_config == {
        'begin_ml_comment': '/*',
        'end_ml_comment': '*/',
        'allow_sl_comments': False,
        'sl_comment': '//',
    }

# Test DEFAULT_CONFIG dictionary structure


def test_default_config_structure():
    assert isinstance(DEFAULT_CONFIG, dict)
    assert 'main' in DEFAULT_CONFIG
    assert 'output' in DEFAULT_CONFIG
    assert 'parser' in DEFAULT_CONFIG

    assert 'meta' in DEFAULT_CONFIG['main']
    assert 'dir' in DEFAULT_CONFIG['output']
    assert 'type' in DEFAULT_CONFIG['output']
    assert 'begin_doc' in DEFAULT_CONFIG['parser']
    assert 'end_doc' in DEFAULT_CONFIG['parser']

# Test the parser configuration for specific languages in DEFAULT_CONFIG


def test_default_parser_config_languages():
    parser_config = DEFAULT_CONFIG['parser']

    # Check Python configuration
    assert 'py' in parser_config
    assert parser_config['py']['begin_ml_comment'] == "'''"
    assert parser_config['py']['end_ml_comment'] == "'''"
    assert not parser_config['py']['allow_sl_comments']

    # Check C++ configuration (and similar extensions)
    for lang in ['c', 'cpp', 'cc', 'h', 'hpp']:
        assert lang in parser_config
        assert parser_config[lang] == _c_like_languages_parser_config

    # Check Rust configuration
    assert 'rs' in parser_config
    assert parser_config['rs'] == _c_like_languages_parser_config

# Test index_file_dir when no main section is defined


def test_index_file_dir_no_main_section():
    config = {}
    with patch('builtins.print') as mock_print:
        result = index_file_dir(config)
        assert result == '{index-file-dir}'
        mock_print.assert_called_once_with(
            'Warning: using variable index-file-dir before defining `main` section in config file')

# Test index_file_dir when index_file is missing in the main section


def test_index_file_dir_no_index_file():
    config = {'main': {}}
    with patch('builtins.print') as mock_print:
        result = index_file_dir(config)
        assert result == '{index-file-dir}'
        mock_print.assert_called_once_with(
            'Warning: using variable index-file-dir before defining `index_file` in `main` section in config file')

# Test index_file_dir with a valid index_file path


def test_index_file_dir_with_valid_index_file():
    config = {'main': {'index_file': '/path/to/index.md'}}

    # Mock os.path.abspath and os.path.dirname to return controlled values
    with patch('os.path.abspath', return_value='/path/to'), \
            patch('os.path.dirname', return_value='/path/to'):
        result = index_file_dir(config)
        assert result == '/path/to'

# Test index_file_dir with an empty path returned from os.path.abspath


def test_index_file_dir_with_empty_abspath():
    config = {'main': {'index_file': '/path/to/index.md'}}

    # Mock os.path.abspath to return an empty string, and os.path.dirname to
    # return a valid path
    with patch('os.path.abspath', return_value=''), \
            patch('os.path.dirname', return_value='/path/to'):
        result = index_file_dir(config)
        assert result == './'

# Test PREDEFINED_VARIABLES contains correct mapping


def test_predefined_variables():
    assert 'index-file-dir' in PREDEFINED_VARIABLES
    assert PREDEFINED_VARIABLES['index-file-dir'] == index_file_dir
