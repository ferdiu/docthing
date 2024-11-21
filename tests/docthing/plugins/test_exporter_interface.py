# SPDX-License-Identifier: MIT
import pytest
from unittest.mock import MagicMock, patch, mock_open

from docthing.plugins.exporter_interface import Exporter
from docthing.documentation_content import ResourceReference
from docthing.documentation_blob import DocumentationBlob


class MockResourceReference(ResourceReference):
    """
    Mock implementation of the ResourceReference class for testing purposes.
    """

    def compile(self):
        return "compiled_resource"

    def get_ext(self):
        return "mock_ext"


class MockExporter(Exporter):
    """
    Mock implementation of the Exporter class for testing purposes.
    """

    def _export_leaf(self, leaf, output_file_no_ext):
        """
        Mock export logic for leaf nodes.
        """
        with open(f"{output_file_no_ext}.mock", "w") as f:
            f.write(f"Exported leaf: {leaf.get_title()}")

    def import_function(self, leaf_title, resource):
        """
        Mock import logic for external resources.
        """
        return f"imported:{resource}"

    def _disable(self):
        pass

    def _enable(self):
        pass

    def get_dependencies(self):
        return []

    def get_description(self):
        return "mock description"

    def get_name(self):
        return "mock-exporter"


@pytest.fixture
def mock_documentation_blob(tmp_path):
    """
    Fixture to create a mock DocumentationBlob with sample nodes.
    """
    parser_config = {"extensions": ["md"], "iexts": []}
    index_file = tmp_path / "index.json"

    # Write a mock index file
    index_file.write_text(
        """
        {
            "main-title": "Main",
            "quick": "quick.md",
            "intro": "intro.md",
            "Chapter 1": {
                "Section 1.1": "section1_1.md",
                "Section 1.2": "section1_2.md"
            }
        }
        """
    )

    return DocumentationBlob(
        index_file=str(index_file),
        parser_config=parser_config)


@patch("os.makedirs")
@patch("docthing.plugins.exporter_interface.mkdir_silent")
@patch("builtins.open", mock_open(read_data="data"))
def test_export(
        mock_mkdir_silent,
        mock_documentation_blob,
        tmp_path):
    """
    Test the export method of the MockExporter class.
    """
    exporter = MockExporter()
    output_dir = tmp_path / "output"

    # Mock methods on the documentation blob
    mock_documentation_blob.unlazy = MagicMock()
    mock_documentation_blob.is_lazy = MagicMock(return_value=True)
    mock_documentation_blob.get_leaves = MagicMock(
        return_value=[
            MagicMock(
                get_title=MagicMock(return_value="Leaf 1"),
                get_path=MagicMock(return_value=[
                    MagicMock(get_title=MagicMock(return_value="Chapter 1")),
                    MagicMock(get_title=MagicMock(
                        return_value="Section 1.1")),
                ]),
                replace_resources_with_imports=MagicMock(),
                get_content=MagicMock(return_value=[]),
            )
        ]
    )

    # Call the export method
    exporter.export(mock_documentation_blob, str(output_dir))

    # Assertions
    mock_documentation_blob.unlazy.assert_called_once()
    mock_mkdir_silent.assert_any_call(str(output_dir))
    leaf = mock_documentation_blob.get_leaves.return_value[0]
    leaf.replace_resources_with_imports.assert_called_with(
        exporter.import_function)


def test_export_leaf_resources(mock_documentation_blob, tmp_path):
    """
    Test the _export_leaf_resources method.
    """
    exporter = MockExporter()
    leaf = MagicMock(
        get_content=MagicMock(
            return_value=[
                MockResourceReference("img", "path/to/resource"),
                "Some text",
                MockResourceReference("img", "path/to/another_resource"),
            ]
        )
    )
    output_file_no_ext = tmp_path / "exported_leaf"

    # Mock the MockResourceReference write method
    with patch.object(MockResourceReference, "write") as mock_write:
        exporter._export_leaf_resources(leaf, str(output_file_no_ext))

        # Assertions
        assert mock_write.call_count == 2
        mock_write.assert_any_call(str(output_file_no_ext))


def test_import_function():
    """
    Test the import_function method of MockExporter.
    """
    exporter = MockExporter()
    result = exporter.import_function("Leaf Title", "Resource")
    assert result == "imported:Resource"
