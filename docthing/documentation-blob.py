

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
