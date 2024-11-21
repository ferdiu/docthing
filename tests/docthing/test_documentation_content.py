# SPDX-License-Identifier: MIT

# test_resource_document.py
import pytest
import re

from docthing.documentation_content import ResourceReference, Document
from docthing.util import sha256sum


# Concrete implementation of ResourceReference for testing purposes

class TestResourceReference(ResourceReference):
    __test__ = False

    def get_ext(self):
        return 'txt'

    def compile(self, output_prefix):
        return 'compiled_content'


# Tests for ResourceReference

class TestResourceReferenceClass:
    def test_search_valid_reference(self):
        line = '@ref(type1)-->[path/to/resource]'
        assert ResourceReference.search(line) == ('type1', 'path/to/resource')

    def test_search_invalid_reference(self):
        line = 'Invalid reference'
        assert ResourceReference.search(line) is None

    def test_init_with_hash(self):
        source = ['line1', 'line2']
        ref = TestResourceReference(source, 'type1', use_hash=True)
        expected_hash = sha256sum(''.join(source))
        assert ref.get_hash() == expected_hash

    def test_init_without_hash(self):
        ref = TestResourceReference(['line1'], 'type1', use_hash=False)
        assert ref.get_hash() is None

    def test_init_with_custom_hash(self):
        custom_hash = 'custom_hash'
        ref = TestResourceReference(['line1'], 'type1', use_hash=custom_hash)
        assert ref.get_hash() == custom_hash

    def test_init_invalid_hash(self):
        with pytest.raises(ValueError, match='use_hash must be a boolean or a string'):
            TestResourceReference(['line1'], 'type1', use_hash=123)

    def test_get_path_with_hash(self):
        source = ['line1']
        ref = TestResourceReference(source, 'type1', use_hash=True)
        expected_hash = sha256sum(''.join(source))
        assert ref.get_path() == f'{expected_hash}.txt'

    def test_get_path_without_hash(self):
        ref = TestResourceReference(['line1'], 'type1', use_hash=False)
        assert ref.get_path() == '.txt'

    def test_get_path_with_custom_hash(self):
        custom_hash = 'custom_string'
        ref = TestResourceReference(['line1'], 'type1', use_hash=custom_hash)
        assert ref.get_path() == f'{custom_hash}.txt'

    def test_str_representation(self):
        ref = TestResourceReference(['line1'], 'type1', use_hash=False)
        assert str(ref) == '@ref(type1)-->[.txt]\n'


# Tests for Document

class TestDocument:
    def test_init_empty(self):
        doc = Document()
        assert doc.content == []

    def test_init_with_string(self):
        doc = Document('line1\nline2')
        assert doc.content == ['line1\n', 'line2']

    def test_init_with_list(self):
        content = ['line1\n', 'line2']
        doc = Document(content)
        assert doc.content == content

    def test_init_invalid_content(self):
        with pytest.raises(ValueError, match='content must be a list of strings or ResourceReferences'):
            Document(123)

    def test_replace_lines_with_reference(self):
        content = ['line1\n', 'line2\n', 'line3\n']
        ref = TestResourceReference(['source'], 'type1')
        doc = Document(content)
        doc.replace_lines_with_reference(ref, 1, 2)
        assert doc.content == ['line1\n', ref]

    def test_replace_lines_with_reference_invalid_reference(self):
        doc = Document(['line1', 'line2'])
        with pytest.raises(ValueError, match='reference must be a ResourceReference'):
            doc.replace_lines_with_reference('invalid', 0, 1)

    def test_replace_lines_with_reference_invalid_indices(self):
        doc = Document(['line1', 'line2'])
        ref = TestResourceReference(['source'], 'type1')
        with pytest.raises(ValueError, match='begin and end must be integers'):
            doc.replace_lines_with_reference(ref, 'a', 1)

    def test_replace_resources_with_imports(self):
        def mock_import_function(title, el):
            return f'imported_{el}'

        doc = Document(['@ref(type1)-->[path/to/resource]', 'normal line'])
        doc.replace_resources_with_imports('Title', mock_import_function)
        assert doc.content == [
            'imported_@ref(type1)-->[path/to/resource]', 'normal line']

    def test_prepend_resource(self):
        doc = Document(['line1', 'line2'])
        doc.prepend_resource('new line')
        assert doc.content == ['new line', 'line1', 'line2']

    def test_append_resource(self):
        doc = Document(['line1', 'line2'])
        doc.append_resource('new line')
        assert doc.content == ['line1', 'line2', 'new line']

    def test_get_printable(self):
        content = ['line1\n', TestResourceReference(['source'], 'type1')]
        doc = Document(content)

        assert re.match(
            'line1\n@ref\\(type1\\)-->\\[[0-9a-f]{64}\\.txt\\]\n',
            doc.get_printable()) is not None

    def test_str_representation(self):
        content = ['line1\n', TestResourceReference(['source'], 'type1')]
        doc = Document(content)
        assert str(doc) == 'Document(1 lines, 1 references)'
