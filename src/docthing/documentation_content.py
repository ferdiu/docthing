

from abc import ABC, abstractmethod

from docthing.util import sha256sum


class ResourceReference(ABC):
    '''
    A class that represents a reference to a resource.
    '''

    def __init__(self, path, type, compile_to=None):
        self.path = path
        self.type = type
        self.compile_to = compile_to

    def need_compilation(self):
        return self.compile_to is not None

    @abstractmethod
    def _compile(self):
        pass

    def compile(self):
        if self.need_compilation():
            self._compile()

    def __str__(self):
        return f'@ref({self.type})-->[{self.path}]-->' + \
            '{' + self.compile_to + '}'


class CodeReference(ResourceReference):
    '''
    A class that represents a reference to a code resource.
    '''
    def __init__(self, path, type, source_code, compiled_ext):
        self.source_code = source_code
        self.path = path
        self.hash = sha256sum(''.join(source_code))
        super().__init__(path, type, self.hash + '.' + compiled_ext)


class Document():
    '''
    A wrapper class for a list of strings or `ResourceReference`s.
    '''

    def __init__(self, content):
        if not Document.can_be(content):
            raise ValueError(
                'content must be a list of strings or ResourceReferences')
        self.content = content

    def can_be(vec):
        if not isinstance(vec, list):
            return False
        for el in vec:
            if not isinstance(
                    el,
                    ResourceReference) and not isinstance(
                    el,
                    str):
                return False
        return True

    def __str__(self):
        line_count = 0
        ref_count = 0
        for el in self.content:
            if isinstance(el, ResourceReference):
                ref_count += 1
            else:
                line_count += 1
        return f'Document({line_count} lines, {ref_count} references)'
