
from abc import ABC


class TreeNode(ABC):
    '''
    The `TreeNode` class is an abstract base class that represents a node in a tree
    data structure. It provides methods for managing the parent-child relationships
    between nodes, such as setting the parent, adding and removing children, and retrieving
    information about the node's position in the tree.

    The `is_root()` method returns `True` if the node has no parent, indicating that it
    is the root of the tree. The `get_parent()` and `set_parent()` methods allow you
    to retrieve and update the node's parent, respectively. The `is_leaf()` method returns
    `True` if the node has no children.

    The `add_child()` method adds a new child node to the current node, and the `get_children()`
    and `get_child()` methods allow you to retrieve the node's children. The `remove_child()`
    method removes a child node from the current node.
    '''

    def __init__(self, parent=None, children=None):
        '''
        Initialize a new TreeNode instance.
        '''
        self.parent = parent
        self.children = children if children is not None else []

    def is_root(self):
        '''
        Check if the node is the root of the tree.
        '''
        return self.parent is None

    def get_parent(self):
        '''
        Get the parent node of the current node.
        '''
        return self.parent

    def set_parent(self, parent):
        '''
        Set the parent node of the current node.
        '''
        if self.parent is not None:
            self.parent.remove_child(self)
        self.parent = parent

    def is_leaf(self):
        '''
        Check if the node is a leaf node (i.e., has no children).
        '''
        return len(self.children) == 0

    def add_child(self, child):
        '''
        Add a child node to the current node.
        '''
        child.set_parent(self)
        self.children.append(child)

    def get_children(self):
        '''
        Get the children of the current node.
        '''
        return self.children

    def get_child(self, index):
        '''
        Get the child node at the specified index.
        '''
        if index < 0 or index >= len(self.children):
            raise IndexError('Index out of range')
        return self.children[index]

    def remove_child(self, index):
        '''
        Remove the child node at the specified index.
            If index is a `TreeNode`, remove the child node.
        '''
        if isinstance(index, int):
            if index < 0 or index >= len(self.children):
                raise IndexError('Index out of range')
            child = self.children[index]
            self.children.remove(child)
            child.set_parent(None)
            return child
        elif isinstance(index, TreeNode):
            if index not in self.children:
                raise ValueError('Child not found in the tree')
            child = index
            self.children.remove(child)
            child.set_parent(None)
            return child
        else:
            raise TypeError('Invalid index type')

    def get_depth(self):
        '''
        Get the depth of the current node in the tree.
        '''
        if self.is_root():
            return 0
        else:
            return 1 + self.parent.get_depth()

    def get_height(self):
        '''
        Get the height of the current node in the tree.
        '''
        if self.is_leaf():
            return 0
        else:
            return 1 + max(child.get_height() for child in self.children)

    def get_size(self):
        '''
        Get the size of the current node in the tree.
        '''
        if self.is_leaf():
            return 1
        else:
            return 1 + sum(child.get_size() for child in self.children)

    def get_path(self):
        '''
        Get the path from the root node to the current node.
        '''
        if self.is_root():
            return [self]
        else:
            return self.parent.get_path() + [self]

    def get_leaves(self):
        '''
        Get the leaves of the current node in the tree.
        '''
        if self.is_leaf():
            return [self]
        else:
            leaves = []
            for child in self.children:
                leaves.extend(child.get_leaves())
            return leaves


class Tree(TreeNode):
    '''
    The `Tree` class is a subclass of `TreeNode` that represents a tree data structure.
    It provides methods for managing the tree structure, such as adding and removing
    nodes, and retrieving information about the tree.

    The `Tree` class has a `root` attribute that represents the root node of the tree.
    The `get_root()` method returns the root node of the tree.
    The `is_root()`, `get_parent()`, `is_leaf()`, `add_child()`, `get_children()`, and
    `get_child()` methods are inherited from the `TreeNode` class and provide functionality
    for managing the tree structure.
    '''

    def __init__(self, root=None):
        '''
        Initialize a new Tree instance.
        '''
        self.root = TreeNode() if root is None else root

    def get_root(self):
        '''
        Get the root node of the tree.
        '''
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

    def get_depth(self):
        return 0

    def get_height(self):
        return self.get_root().get_height()

    def get_size(self):
        return self.get_root().get_size()

    def get_path(self):
        return [self.get_root()]

    def get_leaves(self):
        return self.get_root().get_leaves()
