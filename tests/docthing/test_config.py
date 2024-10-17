# SPDX-License-Identifier: MIT

import pytest
from unittest.mock import patch, mock_open
from docthing.config import _variable_replace_single, merge_configs, load_config
from docthing.config import validate_config, _combine_values, _split_sections_key
from docthing.config import _go_into_scope, _get_var_value, get_as_dot_config


def test_combine_values():
    assert _combine_values('a', 'b') == 'ab'
    assert _combine_values('a', ['b', 'c']) == ['ab', 'ac']
    assert _combine_values(['a', 'b'], 'c') == ['ac', 'bc']
    assert _combine_values(['a', 'b'], ['c', 'd']) == ['ac', 'ad', 'bc', 'bd']


def test_split_sections_key():
    assert _split_sections_key(['a', 'b', 'c']) == (['a', 'b'], 'c')
    assert _split_sections_key(['x']) == ([], 'x')


def test_go_into_scope():
    config = {
        'a': {
            'b': {
                'c': 'value'
            }
        }
    }
    assert _go_into_scope(config, 'a.b') == {'c': 'value'}
    assert _go_into_scope(config, ['a', 'b']) == {'c': 'value'}

    with pytest.raises(ValueError):
        _go_into_scope(config, 123)


def test_get_var_value():
    config = {
        'section1': {
            'subsection': {
                'key': 'value'
            }
        }
    }
    assert _get_var_value(config, 'section1.subsection.key') == 'value'
    assert _get_var_value(config, ['section1', 'subsection', 'key']) == 'value'


def test_variable_replace_single():
    config = {
        'section1': {
            'my_variable': 'actual_value',
            'my_replaceable': '{my_variable}',
            'predefined_var': 'pre-{predefined-var}-post',
            'middle_replace': 'pre-{my_variable}-post',
            'nested': {
                'missing_variable': '{non_existing_variable}',
            },
        },
        'section2': {
            'nested': {
                'key': 'nested_value',
                'next_to_key': '{key}',
            },
        },
    }

    mock_predefined_variables = {
        'predefined-var': lambda config: 'replaced_value'
    }

    # Test simple replacement
    result = _variable_replace_single(
        config, 'section1.my_replaceable')
    assert result == 'actual_value'

    # Test replacement within other values
    result = _variable_replace_single(config, 'section1.middle_replace')
    assert result == 'pre-actual_value-post'

    # Test nested variable replacement
    result = _variable_replace_single(config, 'section2.nested.key')
    assert result == 'nested_value'

    # Test predefined variable replacement
    with patch('docthing.config.PREDEFINED_VARIABLES', mock_predefined_variables):
        result = _variable_replace_single(
            config, 'section1.predefined_var')
        assert result == 'pre-replaced_value-post'

    # Test when variable is not found
    result = _variable_replace_single(
        config,
        'section1.nested.missing_variable')
    assert result == '{non_existing_variable}'

    # Test scoped variable replacement
    result = _variable_replace_single(
        config,
        'section2.nested.next_to_key')
    assert result == 'nested_value'


def test_merge_configs():
    config1 = {
        'main': {
            'key1': 'value1',
            'nested': {
                'key2': 'value2'
            }
        }
    }
    config2 = {
        'main': {
            'nested': {
                'key2': 'new_value2',
                'key3': 'value3'
            }
        },
        'extra': {
            'key4': 'value4'
        }
    }

    merged = merge_configs(config1, config2)

    expected = {
        'main': {
            'key1': 'value1',
            'nested': {
                'key2': 'new_value2',
                'key3': 'value3'
            }
        },
        'extra': {
            'key4': 'value4'
        }
    }
    assert merged == expected


def test_load_config():
    config_path = 'dummy_path.conf'
    mock_config_file = '''
    [main]
    index_file = test_index.jsonc
    extensions = .html, .txt

    [output]
    dir = output_dir
    type = html

    [parser]
    begin_doc = <!--start-->
    end_doc = <!--end-->
    doc_level = 1
    '''
    command_line_config = {'main': {'index_file': 'command_line_index.jsonc'}}

    with patch('builtins.open', mock_open(read_data=mock_config_file)):
        with patch('os.path.exists', return_value=True):
            config = load_config(config_path, command_line_config)

    expected_config = {
        'main': {
            'index_file': 'command_line_index.jsonc',
            'extensions': ['.html', '.txt'],
        },
        'output': {
            'dir': 'output_dir',
            'type': 'html'
        },
        'parser': {
            'begin_doc': '<!--start-->',
            'end_doc': '<!--end-->',
            'doc_level': 1
        }
    }
    assert config == expected_config


def test_validate_config():
    valid_config = {
        'main': {
            'index_file': 'index.jsonc',
        },
        'output': {
            'dir': 'output_directory',
            'type': 'html'
        },
        'parser': {
            'begin_doc': '<!--start-->',
            'end_doc': '<!--end-->',
            'doc_level': 1,
            'extensions': ['.html', '.txt']
        }
    }

    # Should pass without raising an exception
    validated_config = validate_config(valid_config)
    assert validated_config == valid_config

    invalid_config = {
        'main': {
            'index_file': 'index.jsonc'
        },
        'output': {
            'dir': 'output_directory'
            # Missing 'type' key
        }
    }

    with pytest.raises(Exception):
        validate_config(invalid_config)


def test_simple_config():
    config = {
        'main': {
            'index_file': 'docthing.jsonc',
            'extensions': 'js,jsx,ts,tsx'
        }
    }
    output = get_as_dot_config(config)
    assert '[main]' in output
    assert 'index_file=docthing.jsonc' in output
    assert 'extensions=js,jsx,ts,tsx' in output


def test_nested_config():
    config = {
        'parser': {
            'begin_doc': 'BEGIN FILE DOCUMENTATION',
            'js': {
                'begin_ml_comment': '/*',
                'end_ml_comment': '*/'
            }
        }
    }
    output = get_as_dot_config(config)
    assert '[parser]' in output
    assert 'begin_doc=BEGIN FILE DOCUMENTATION' in output
    assert '[parser|js]' in output
    assert 'begin_ml_comment=/*' in output
    assert 'end_ml_comment=*/' in output


def test_multiple_sections():
    config = {
        'main': {'index_file': 'docthing.jsonc'},
        'output': {'dir': './documentation'},
        'parser': {'doc_level': 1}
    }
    output = get_as_dot_config(config)
    assert '[main]' in output
    assert '[output]' in output
    assert '[parser]' in output
    assert 'index_file=docthing.jsonc' in output
    assert 'dir=./documentation' in output
    assert 'doc_level=1' in output


def test_empty_config():
    config = {}
    output = get_as_dot_config(config)
    assert output.strip() == ''


def test_main_section_without_index_file():
    config = {
        'main': {
            'extensions': 'js,jsx,ts,tsx'
        }
    }
    output = get_as_dot_config(config)
    assert '[main]' in output
    assert 'index_file=' in output
    assert 'extensions=js,jsx,ts,tsx' in output
