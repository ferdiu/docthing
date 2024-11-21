# SPDX-License-Identifier: MIT

# test_utils.py
import os
import hashlib
import pathlib
import sys
import pytest
from unittest.mock import patch

from docthing.util import mkdir_silent, parse_value, sha256sum
from docthing.util import get_datadir, get_docthing_datadir, get_docthing_plugin_dir


# Test mkdir_silent

def test_mkdir_silent(tmp_path):
    test_dir = tmp_path / "test_dir"
    mkdir_silent(test_dir)
    assert test_dir.exists()
    assert test_dir.is_dir()


def test_mkdir_silent_existing(tmp_path):
    test_dir = tmp_path / "existing_dir"
    os.makedirs(test_dir)
    mkdir_silent(test_dir)  # Should not raise an exception
    assert test_dir.exists()


# Test parse_value

@pytest.mark.parametrize("input_value, expected", [
    ("true", True),
    ("false", False),
    ("null", None),
    ("none", None),
    ("42", 42),
    ("3.14", 3.14),
    ("a,b,c", ["a", "b", "c"]),
    ("1,2,3", [1, 2, 3]),
    ("", ""),
    ("hello", "hello"),
])
def test_parse_value(input_value, expected):
    assert parse_value(input_value) == expected


# Test sha256sum

def test_sha256sum():
    test_string = "hello world"
    expected_hash = hashlib.sha256(test_string.encode()).hexdigest()
    assert sha256sum(test_string) == expected_hash


# Test get_datadir

def test_get_datadir_linux(monkeypatch):
    monkeypatch.setattr(sys, "platform", "linux")
    home = pathlib.Path.home()
    expected = home / ".local/share"
    assert get_datadir() == expected


def test_get_datadir_windows(monkeypatch):
    monkeypatch.setattr(sys, "platform", "win32")
    home = pathlib.Path.home()
    expected = home / "AppData/Roaming"
    assert get_datadir() == expected


def test_get_datadir_mac(monkeypatch):
    monkeypatch.setattr(sys, "platform", "darwin")
    home = pathlib.Path.home()
    expected = home / "Library/Application Support"
    assert get_datadir() == expected


# Test get_docthing_datadir

def test_get_docthing_datadir(monkeypatch):
    mock_datadir = pathlib.Path("/mock/datadir")
    with patch("docthing.util.get_datadir", return_value=mock_datadir):
        assert get_docthing_datadir() == mock_datadir / "docthing"


# Test get_docthing_plugin_dir

def test_get_docthing_plugin_dir_valid_type(monkeypatch):
    mock_datadir = pathlib.Path("/mock/datadir")
    with patch("docthing.util.get_datadir", return_value=mock_datadir):
        assert get_docthing_plugin_dir(
            "meta-interpreter") == mock_datadir / "docthing/plugins/meta-interpreter"


def test_get_docthing_plugin_dir_invalid_type(monkeypatch):
    mock_datadir = pathlib.Path("/mock/datadir")
    with patch("docthing.util.get_datadir", return_value=mock_datadir):
        with pytest.raises(ValueError, match="Plugin type not supported."):
            get_docthing_plugin_dir("unsupported_type")
