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

from .index import process_index
from .tree import Tree, TreeNode


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

    def __init__(self, title, content=None, children=None):
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
        if content is not None and children is not None or content is None and children is None:
            raise ValueError(
                "Either content or children must be provided, but not both.")

        self.title = title
        self.content = content
        self.children = children if children is not None else []

    def get_content(self):
        '''
        Get the content of the node (str).
        '''
        return self.content


class DocumentationBlob(Tree):
    '''
    DocumentationBlob is a class that represents a blob of documentation.
        It contains the entire project documentation documentation in a output agnostic way.
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

        with open(index_file, 'r') as f:
            self.index_file = json.load(f)

        super().__init__(self._generate_tree_from_index(self.index_file).get_root())

    def _generate_tree_from_index(self, index_file_json):
        # It is ok to iterate over dict keys since python 3.6
        # see:
        # https://docs.python.org/3/whatsnew/3.6.html#whatsnew36-compactdict
        return Tree(self._generate_root(self, index_file_json))

    def _generate_root(self, index_file_json):
        if 'main-title' not in index_file_json:
            raise ValueError("Index file must contain 'main-title'")

        res = DocumentationNode(index_file_json['main-title'])

        if 'intro' not in index_file_json:
            print(
                '''Warning: index file does not contain 'intro': this is discouraged: it is
                  important to give the user a brief introduction to the project''')
        else:
            res.add_child(self._generate_leaf(index_file_json['intro']))
        if 'quick' not in index_file_json:
            print(
                '''Warning: index file does not contain 'quick': this is discouraged: it is
                  important to give the user a grasp of the usage of the project''')
        else:
            res.add_child(self._generate_leaf(index_file_json['quick']))

        return res

    def _generate_internal_node(self, title, content_file_path):
        return DocumentationNode(title, )

    def _generate_leaf(self):
        pass

    def _generate_node(self, node):
        if node.get('type') == 'chapter':
            return DocumentationNode(
                node['title'], self._generate_tree_from_index(
                    node['content']).get_root())
        elif node.get('type') == 'section':
            return DocumentationNode(
                node['title'], self._generate_tree_from_index(
                    node['content']).get_root())
        elif node.get('type') == 'file':
            return DocumentationNode(
                node['title'], self._generate_tree_from_index(
                    node['content']).get_root())
        elif node.get('type') == 'directory':
            return DocumentationNode(
                node['title'], self._generate_tree_from_index(
                    node['content']).get_root())
        elif node.get('type') == 'file_list':
            return DocumentationNode(
                node['title'], self._generate_tree_from_index(
                    node['content']).get_root())
        elif node.get('type') == 'file_list_item':
            return DocumentationNode(
                node['title'], self._generate_tree_from_index(
                    node['content']).get_root())


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
