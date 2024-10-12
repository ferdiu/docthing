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

import json
import os

from .tree import Tree, TreeNode
from abc import ABC, abstractmethod


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


class DocumentationNode(TreeNode):
    '''
    A node in the documentation tree, representing a chapter, section, file, directory,
    or file list.

    The `DocumentationNode` class represents a node in the documentation tree, which can be
    a chapter, section, file, directory, or file list. Each node has a title and either
    content or a list of child nodes.

        Args:
            title (str): The title of the node.
            content (str, optional): The content of the node, if it is a file.
            children (list, optional): A list of child nodes, if the node is a chapter, section,
            directory, or file list.

        Raises:
            ValueError: If both `content` and `children` are provided, or if neither is provided.
    '''

    def __init__(self, parent, title, content=None, children=None):
        '''
        Initialize a new DocumentationNode.

            Args:
                title (str): The title of the node.
                content (str, optional): The content of the node, if it is a file.
                children (list, optional): A list of child nodes, if the node is a chapter,
                section, directory, or file list.

            Raises:
                ValueError: If both `content` and `children` are provided, or if neither is
                provided.
        '''
        super().__init__(parent, children)

        if content is not None and children is not None:
            raise ValueError('Both content and children cannot be provided')

        if content is not None and not isinstance(
                content, str) and not isinstance(
                content, ResourceReference):
            raise ValueError(
                'content must be None, a path to a file or a ResourceReference')

        self.title = title
        self.content = content

        self.lazy = isinstance(
            content, str) and (
            os.path.isfile(content) or os.path.isdir(content))

    def is_lazy(self):
        '''
        Check if the node is lazy.

            Returns:
                bool: True if the node is lazy, False otherwise.
        '''
        return self.lazy

    def _unlazy_content(self):
        '''
        Unlazy the content of the node.

            Raises:
                    ValueError: If the content of the node is not a file or a directory.
        '''
        if not self.lazy:
            return

        if os.path.isfile(self.content):
            with open(self.content, 'r') as f:
                self.content = f.read()
        elif os.path.isdir(self.content):
            self.content = self.content
        else:
            raise ValueError(
                f'The content of the node {
                    self.title} is not a file or a directory.')
        self.lazy = False

    def get_content(self, unlazy=False):
        '''
        Get the content of the node.

            Args:
                unlazy (bool, optional): If True, the content of the node will be unlazy.
                    Defaults to False.
                    If False, the content of the node will be returned as is.
                    If True, the content of the node will be unlazy and returned.
                    If the content of the node is not a file or a directory,
                    a ValueError will be raised.
            Returns:
                str: The content of the node.
        '''
        if not self.lazy or not unlazy:
            return self.content

        if unlazy:
            self._unlazy_content()
            return self.content

    def get_title(self):
        '''
        Get the title of the node.

            Returns:
                str: The title of the node.
        '''
        return self.title

    def __str__(self) -> str:
        if not self.lazy and self.is_leaf():
            return __class__.__name__ + \
                '(' + self.title + ', ' + str(self.content) + ')'
        else:
            return __class__.__name__ + '(' + self.title + ')'


class DocumentationBlob(Tree):
    '''
    DocumentationBlob is a class that represents a blob of documentation.
        It contains the entire project documentation in a output agnostic way.
        It can be used to generate documentation in various formats.
    '''

    def __init__(
            self,
            index_file,
            parser_config,
            extensions,
            ignored_extensions):
        self.parser_config = parser_config
        self.extensions = extensions
        self.ignored_extensions = ignored_extensions
        self.index_file_path = index_file

        super().__init__(self._generate_tree_from_index())

    def _generate_tree_from_index(self):
        return self._generate_node_from_index(None, self.index_file_path)

    def _generate_node_from_index(self, parent, index_file_json):
        '''
        Generate the root node of the tree.
        '''
        with open(index_file_json, 'r') as f:
            index_file_json = json.load(f)

        # Main title
        if 'main-title' not in index_file_json:
            raise ValueError('Index file must contain \'main-title\'')

        res = DocumentationNode(parent, index_file_json['main-title'])

        # Introduction
        if 'intro' not in index_file_json:
            print('Warning: index file does not contain \'intro\': this is discouraged: it is ' +
                  'important to give the user a brief introduction to the project')
        else:
            res.add_child(
                self._generate_leaf(
                    parent,
                    'Introduction',
                    index_file_json['intro']))

        # Quick Start
        if 'quick' not in index_file_json:
            print('Warning: index file does not contain \'quick\': this is discouraged: it is ' +
                  'important to give the user a grasp of the usage of the project')
        else:
            res.add_child(
                self._generate_leaf(
                    parent,
                    'Quick Start',
                    index_file_json['quick']))

        # It is ok to iterate over dict keys since python 3.6
        # see:
        # https://docs.python.org/3/whatsnew/3.6.html#whatsnew36-compactdict
        for k, v in index_file_json.items():
            if k not in ['main-title', 'intro', 'quick']:
                res.add_child(self._generate_node(parent, k, v))

        return res

    def _generate_internal_node(self, parent, title, children):
        '''
        Generate a node with children.
        '''
        if isinstance(children, dict):
            return DocumentationNode(parent, title, None,
                                     [self._generate_node(parent, child_title, child)
                                      for child_title, child in children.items()])
        else:
            return DocumentationNode(parent, title, None,
                                     [self._generate_node(parent, '', child)
                                      for child in children])

    def _generate_leaf(self, parent, title, content_file_path):
        '''
        Generate a leaf node.
        '''
        return DocumentationNode(parent, title, content_file_path)

    def _generate_node(self, parent, title, node):
        '''
        Generate a node.
        '''
        if title == '__index__':
            return self._generate_node_from_index(parent, node)
        elif isinstance(node, dict):
            return self._generate_internal_node(parent, title, node)
        elif isinstance(node, list):
            return self._generate_internal_node(parent, title, node)
        elif isinstance(node, str):
            return self._generate_leaf(parent, title, node)
        raise ValueError('Invalid node type')


# array
#   title: from chapter/section
#   children: concatenation of the content of all the nodes

# intro
#   title: Introduction
#   content: content of the file pointed by the intro field

# quick
#   title: Quick Start
#   content: content of the file pointed by the quick field

# dictionary
#   title: from chapter/section
#   children:
