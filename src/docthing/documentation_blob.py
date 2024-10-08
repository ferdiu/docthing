''' BEGIN FILE DOCUMENTATION (level: 2)
Everything in `docthing` is about the class [`DocumentationBlob`](@DocumentationBlob).

This class is the one create after the _index file_ is processed accordingly to the _configuration_.

It contains the entire project documentation documentation in a output agnostic way and it can be
used to generate documentation in various formats.

To export the documentation in a specific format, you can use an `Exporter Plugin` which is a
class that implements the [`Exporter`](@Exporter) abstract class.
After being correctly instantiated, a DocumentationBlob can be exported to a specific format passing
it to the constructor of the `Exporter` implementation.
END FILE DOCUMENTATION '''


class DocumentationBlob:
    '''
    DocumentationBlob is a class that represents a blob of documentation.
        It contains the entire project documentation documentation in a output agnostic way.
        It can be used to generate documentation in various formats.
    '''

    def __init__(self, index_file, config):
        self.index_file = index_file
        self.config = config


class DocumentationNode(object):
    def __init__(self, title, content, children=None):
        self.title = title
        self.content = content
        self.children = children if children is not None else []


class DocumentationLeaf(object):
    def __init__(self, title, content):
        self.title = title
        self.content = content
