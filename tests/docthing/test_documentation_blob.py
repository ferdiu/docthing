# SPDX-License-Identifier: MIT

import pytest
import os
from unittest.mock import MagicMock  # , patch
from typing import Union

from docthing.documentation_blob import DocumentationNode  # , DocumentationBlob
from docthing.documentation_content import Document, ResourceReference


# Mock and fixtures

@pytest.fixture
def mock_config():
    return {
        "extensions": ["md", "txt"],
        "iexts": [],
        "doc_level": 1
    }


@pytest.fixture
def mock_index_file():
    return "index.json"


# Documentation Node

def test_initialize_leaf_node(mock_config, monkeypatch):
    monkeypatch.setattr(os.path, "isfile", lambda x: True)
    node = DocumentationNode(
        parent=None,
        title="Leaf Node",
        content="content.md",
        parser_config=mock_config
    )
    assert node.get_title() == "Leaf Node"
    assert node.get_content() == "content.md"
    assert node.is_lazy()


def test_initialize_internal_node(mock_config):
    child = DocumentationNode(
        parent=None,
        title="Child Node",
        content="child.md",
        parser_config=mock_config
    )
    parent = DocumentationNode(
        parent=None,
        title="Parent Node",
        children=[child]
    )
    assert not parent.is_leaf()
    assert parent.get_title() == "Parent Node"


def test_unlazy_content_file(mock_config, monkeypatch):
    monkeypatch.setattr(os.path, "isfile", lambda x: True)
    node = DocumentationNode(
        parent=None,
        title="Lazy Node",
        content="test_file.md",
        parser_config=mock_config
    )
    extract_documentation = MagicMock(
        return_value=(["Extracted Content"], {"level": 1}))
    monkeypatch.setattr(
        "docthing.documentation_blob.extract_documentation",
        extract_documentation)

    node._unlazy_content()

    assert node.get_content().content == ["Extracted Content"]
    assert not node.is_lazy()


# def test_unlazy_content_directory(mock_config, monkeypatch):
#     monkeypatch.setattr(os.path, "isdir", lambda x: True)
#     monkeypatch.setattr(os, "listdir", lambda x: ["file1.md", "file2.txt"])
#     node = DocumentationNode(
#         parent=None,
#         title="Lazy Dir Node",
#         content="test_dir",
#         parser_config=mock_config
#     )
#     extract_documentation = MagicMock(
#         side_effect=(["File 1 Content"], {"level": 1})
#     )
#     monkeypatch.setattr(
#         "docthing.documentation_blob.extract_documentation",
#         extract_documentation)

#     node._unlazy_content()

#     assert isinstance(node.get_content(), Document)
#     assert node.get_content().content
#     assert len(node.get_content().content) == 2


def test_get_options(mock_config, monkeypatch):
    monkeypatch.setattr(os.path, "isfile", lambda x: True)
    node = DocumentationNode(
        parent=None,
        title="Option Node",
        content="test.md",
        parser_config=mock_config
    )
    extract_documentation = MagicMock(
        return_value=(["Content"], {"level": 2, "level-only": True}))
    monkeypatch.setattr(
        "docthing.documentation_blob.extract_documentation",
        extract_documentation)

    node._unlazy_content()

    assert node.get_options() == {"level": 2, "level-only": True}


def test_invalid_content_and_children(mock_config):
    with pytest.raises(ValueError):
        DocumentationNode(
            parent=None,
            title="Invalid Node",
            content="content.md",
            children=[]
        )


class MockReference(ResourceReference):
    def __init__(self, path_to_file):
        super().__init__(None, 'import-file', use_hash=path_to_file)

    def get_ext(self):
        return 'ext'

    def compile(self) -> Union[bytes, str]:
        return None


def test_replace_resources_with_imports(mock_config):
    node = DocumentationNode(
        parent=None,
        title="Replace Resources",
        content=Document([MockReference("resource.ext")]),
        parser_config=mock_config
    )
    mock_import = MagicMock()
    node.replace_resources_with_imports(mock_import)
    mock_import.assert_called()


# Documentation Blob

# @patch("builtins.open", create=True)
# @patch("json.load")
# def test_generate_tree_from_index(
#         mock_json_load,
#         mock_open,
#         mock_config,
#         mock_index_file):
#     mock_json_load.return_value = {
#         "main-title": "Main Title",
#         "intro": "intro.md",
#         "quick": "quick.md",
#         "extra": {
#             "Section": "section.md"
#         }
#     }
#     blob = DocumentationBlob(mock_index_file, mock_config)

#     assert blob.root.get_title() == "Main Title"
#     assert len(blob.root.get_children()) == 3


# def test_unlazy_blob(mock_index_file, mock_config):
#     mock_node = MagicMock(spec=DocumentationNode)
#     mock_node.is_lazy.return_value = True

#     blob = DocumentationBlob(mock_index_file, mock_config)
#     blob.root = mock_node

#     blob.unlazy()

#     mock_node.unlazy.assert_called_once()


# def test_prune_doc(mock_index_file, mock_config):
#     mock_node = MagicMock(spec=DocumentationNode)
#     mock_node.get_content.return_value = "test content"
#     mock_node.get_options.return_value = {"level": 3, "level-only": False}

#     blob = DocumentationBlob(mock_index_file, mock_config)
#     blob.root = mock_node

#     blob.prune_doc()

#     mock_node.unlazy.assert_called_once()


# @patch("builtins.open", create=True)
# @patch("json.load")
# def test_invalid_index_file(
#         mock_json_load,
#         mock_open,
#         mock_config,
#         mock_index_file):
#     mock_json_load.side_effect = ValueError

#     with pytest.raises(ValueError):
#         DocumentationBlob(mock_index_file, mock_config)
