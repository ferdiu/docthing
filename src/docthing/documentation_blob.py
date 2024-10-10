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
from abc import ABC, abstractmethod

from .index import process_index


class TreeNode(ABC):
    def __init__(self, parent=None, children=None):
        self.parent = parent
        self.children = children if children is not None else []

    def is_root(self):
        return self.parent is None

    def get_parent(self):
        return self.parent

    def set_parent(self, parent):
        if parent is None and self.parent is not None:
            self.parent.children.remove(self)
        elif parent is not None and self.parent is not None:
            self.parent.children.remove(self)
        self.parent = parent

    def is_leaf(self):
        return len(self.children) == 0

    def add_child(self, child):
        if child.get_parent() is not None:
            child.get_parent().remove_child(child)
        child.set_parent(self)
        self.children.append(child)

    def get_children(self):
        return self.children

    def get_child(self, index):
        if  index < 0 or index >= len(self.children):
            raise IndexError("Index out of range")
        return self.children[index]

    def remove_child(self, index):
        if isinstance(index, int):
            if index < 0 or index >= len(self.children):
                raise IndexError("Index out of range")
            child = self.children[index]
            self.children.remove(child)
            child.set_parent(None)
            return child
        elif isinstance(index, TreeNode):
            if index not in self.children:
                raise ValueError("Child not found in the tree")
            child = index
            self.children.remove(child)
            child.set_parent(None)
            return child
        else:
            raise TypeError("Invalid index type")


class Tree(TreeNode):
    def __init__(self, root):
        self.root = root

    def get_root(self):
        return self.root

    def is_root(self):
        return True

    def get_parent(self):
        return None

    def set_parent(self, parent):
        return self.get_rooot().set_parent(parent)

    def is_leaf(self):
        return self.get_root().is_leaf()

    def add_child(self, child):
        return self.get_root().add_child(child)

    def get_children(self):
        return self.get_root().get_children()

    def get_child(self, index):
        return self.get_root().get_child(index)

class DocumentationBlob(Tree):
    '''
    DocumentationBlob is a class that represents a blob of documentation.
        It contains the entire project documentation documentation in a output agnostic way.
        It can be used to generate documentation in various formats.
    '''

    def __init__(self, index_file, parser_config, extensions, ignored_extensions):
        self.parser_config = parser_config
        self.extensions = extensions
        self.ignored_extensions = ignored_extensions

        with open(index_file, 'r') as f:
            self.index_file = json.load(f)

        super(self._generate_tree_from_index(self.index_file).get_root())

    def _generate_tree_from_index(index_file_json):
        # TODO: implement this (where the magic happens)
        return Tree()


class DocumentationNode(TreeNode):
    def __init__(self, title, content, children=None):
        self.title = title
        self.content = content
        self.children = children if children is not None else []


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
