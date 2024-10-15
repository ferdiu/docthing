# SPDX-License-Identifier: MIT
''' BEGIN FILE DOCUMENTATION (level: 2)
TODO: documentation_content documentation
END FILE DOCUMENTATION '''

import re
from abc import ABC, abstractmethod
from typing import Union

from .util import sha256sum


class ResourceReference(ABC):
    '''
    A class that represents a reference to a resource.
    '''

    def search(line):
        '''
        Searches for a resource reference in the given line.

        If a reference is found, returns a tuple containing the type and the path
        of the resource. Otherwise, returns None.

        If `use_hash` is specified the resulting path generated when creating the
        resource will change; see: documentation of `ResourceReference.get_path()`
        for a more detailed explanation.
        '''
        m = re.search(r'^@ref\((.+)\)-->\[(.+)\]$', line)
        if m is None:
            return None

        return m.group(1), m.group(2)

    def __init__(self, source, type, use_hash=True):
        self.source = source
        self.type = type
        self.compiled = None
        if isinstance(use_hash, bool):
            self.hash = sha256sum(''.join(source)) if use_hash else None
        elif isinstance(use_hash, str):
            self.hash = use_hash
        else:
            raise ValueError('use_hash must be a boolean or a string')

    def get_source(self):
        '''
        Returns the source of the resource.
        '''
        return self.source

    def get_type(self):
        '''
        Returns the type of the resource.
        '''
        return self.type

    def get_hash(self):
        '''
        Returns the hash of the resource.
        '''
        return self.hash

    def get_path(self):
        '''
        Returns the end of the name of the resource output file (after compilation).
        This depends on the value passed to `use_hash` when creating the resource
        reference:

        - if `use_hash` was setted to `True` when creating the resource reference,
        the path will be:
            `_<hash>.<extension>`
            (eg. `_1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef.png`)
        - if `use_hash` was setted to `False` when creating the resource reference,
        the path will be instead:
            `.<extension>`
            (eg. `.png`)
        - if a `string` was passed to `use_hash` when creating the resource reference,
        the path will be instead:
            `<use_hash string>.<extension>`
            (eg. `test_string.png` if 'test_string' was passed to `use_hash`)

        Remember that this is not the final path passed to the compiler, but only
        the ending part of the name of the file that will be generated.
        '''
        res = ''

        if isinstance(self.hash, bool) and self.hash:
            res += '_' + self.get_hash()
        elif isinstance(self.hash, str):
            res += self.hash

        return res + '.' + self.get_ext()

    @abstractmethod
    def compile(self, output_prefix) -> Union[bytes, str]:
        '''
        Compiles the resource reference.

        Returns the compiled resource reference.
        It can be a string or a bytes object.

        This has to be implemented in a concrete ResourceReference class.
        '''
        pass

    @abstractmethod
    def get_ext(self):
        '''
        Returns the extension of the resource.
        '''
        pass

    def write(self, output_prefix):
        if self.compiled is None:
            self.compiled = self.compile()

        if self.compiled is None:
            # This is the case where the resource reference does not
            #    produce any data.
            return

        mode = 'w+'
        if isinstance(self.compiled, bytes):
            mode = 'wb+'

        with open(output_prefix + self.get_path(), mode) as f:
            f.write(self.compiled)

    def __str__(self):
        return f'@ref({self.get_type()})-->[{self.get_path()}]\n'


class Document():
    '''
    A wrapper class for a list of strings or `ResourceReference`s.
    '''

    def __init__(self, content=None):
        if content is None:
            self.content = []
            return
        if not Document.can_be(content):
            raise ValueError(
                'content must be a list of strings or ResourceReferences')
        if isinstance(content, str):
            self.content = content.splitlines(keepends=True)
        else:
            self.content = content

    def can_be(vec):
        '''
        Returns whether the given vector can be a Document.
        '''
        if isinstance(vec, str):
            return True
        if not isinstance(vec, list):
            return False
        for el in vec:
            if not isinstance(el, ResourceReference) and \
               not isinstance(el, str):
                return False
        return True

    def get_printable(self) -> str:
        if isinstance(self.content, str):
            return self.content
        elif isinstance(self.content, ResourceReference):
            return str(self.content)
        elif isinstance(self.content, list):
            return ''.join([str(c) for c in self.content])
        else:
            raise ValueError('content must be a list of strings or ' +
                             'ResourceReferences')

    def replace_lines_with_reference(self, reference, begin, end):
        '''
        Replace lines between begin and end with a reference.
        '''
        if not isinstance(reference, ResourceReference):
            raise ValueError('reference must be a ResourceReference')

        if end is None:
            end = len(reference.get_source()) - 1

        if not isinstance(begin, int) or not isinstance(end, int):
            raise ValueError('begin and end must be integers')

        if begin < 0 or end < 0:
            raise ValueError('begin and end must be positive')

        if begin > end:
            raise ValueError(
                f'begin must be less than or equal to end: ({begin}, {end})')

        if begin >= len(self.content) or end >= len(self.content):
            raise ValueError(
                'begin and end must be less than the length of the content')

        self.content = self.content[:begin] + \
            [reference] + self.content[end + 1:]

    def replace_resources_with_imports(self, title, import_function):
        for i, el in enumerate(self.content):
            if isinstance(
                    el,
                    ResourceReference) or ResourceReference.search(el):
                self.content[i] = import_function(title, el)

    def prepend_resource(self, resource):
        if isinstance(resource, list):
            for el in resource:
                if not isinstance(el, (ResourceReference, str)):
                    raise ValueError(
                        'resources must be all ResourceReferences or strs')
        elif not isinstance(resource, (ResourceReference, str)):
            raise ValueError('resource must be a ResourceReference or a str')

        if isinstance(resource, list):
            for el in resource:
                self.content.insert(0, el)
        else:
            self.content.insert(0, resource)

    def append_resource(self, resource):
        if isinstance(resource, list):
            for el in resource:
                if not isinstance(el, (ResourceReference, str)):
                    raise ValueError(
                        'resources must be all ResourceReferences or strs')
        elif not isinstance(resource, (ResourceReference, str)):
            raise ValueError('resource must be a ResourceReference or a str')

        if isinstance(resource, list):
            for el in resource:
                self.content.append(el)
        else:
            self.content.append(resource)

    def __iter__(self):
        return iter(self.content)

    def __getitem__(self, index):
        if isinstance(index, (slice, int)):
            return self.content[index]
        elif isinstance(index, tuple):
            return self.content[index[0]:index[1]]

    def __str__(self):
        line_count = 0
        ref_count = 0
        for el in self.content:
            if isinstance(el, ResourceReference):
                ref_count += 1
            else:
                line_count += 1
        return f'Document({line_count} lines, {ref_count} references)'
