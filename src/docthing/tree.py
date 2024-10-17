# SPDX-License-Identifier: MIT

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Union, List, Callable


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

    def __init__(self,
                 parent: Union[None,
                               TreeNode] = None,
                 children: Union[None,
                                 List[TreeNode]] = None):
        '''
        Initialize a new TreeNode instance.
        '''
        self.parent = parent
        self.children = []

        if children is not None:
            for child in children:
                self.add_child(child)

    def is_root(self) -> bool:
        '''
        Check if the node is the root of the tree.
        '''
        return self.parent is None

    def get_parent(self) -> Union[None, TreeNode]:
        '''
        Get the parent node of the current node.
        '''
        return self.parent

    def get_root(self) -> TreeNode:
        '''
        Get the root node of the tree.
        '''
        if self.is_root():
            return self
        else:
            return self.parent.get_root()

    def set_parent(self, parent: Union[None, TreeNode]) -> None:
        '''
        Set the parent node of the current node.
        '''
        if self.parent is not None and self.parent != parent:
            self.parent.remove_child(self)

        # Prevent self-cycling
        if self == parent:
            raise ValueError('A node cannot be its own parent')

        self.parent = parent

    def is_leaf(self) -> bool:
        '''
        Check if the node is a leaf node (i.e., has no children).
        '''
        return len(self.children) == 0

    def add_child(self, child: TreeNode) -> None:
        '''
        Add a child node to the current node.
        '''
        # Prevent self-cycling
        if self == child:
            raise ValueError('A node cannot be its own child')

        child.set_parent(self)
        self.children.append(child)

    def get_children(self) -> List[TreeNode]:
        '''
        Get the children of the current node.
        '''
        return self.children

    def get_child(self, index: int) -> TreeNode:
        '''
        Get the child node at the specified index.
        '''
        if index < 0 or index >= len(self.children):
            raise IndexError('Index out of range')
        return self.children[index]

    def remove_child(self, index: Union[int, TreeNode]) -> TreeNode:
        '''
        Remove the child node at the specified index.
            If index is a `TreeNode`, remove the child node.

            Returns:
                The removed child node.
        '''
        if isinstance(index, int):
            if index < 0 or index >= len(self.children):
                raise IndexError('Index out of range')
            child = self.children[index]
        elif isinstance(index, TreeNode):
            if index not in self.children:
                raise ValueError('Child not found in the tree')
            child = index
        else:
            raise TypeError('Invalid index type')

        self.children.remove(child)
        child.parent = None  # Set the parent to None without triggering `remove_child` again
        return child

    def get_depth(self) -> int:
        '''
        Get the depth of the current node in the tree.
        '''
        if self.is_root():
            return 0
        else:
            return 1 + self.parent.get_depth()

    def get_height(self) -> int:
        '''
        Get the height of the current node in the tree.
        '''
        if self.is_leaf():
            return 0
        else:
            return 1 + max(child.get_height() for child in self.children)

    def get_size(self) -> int:
        '''
        Get the size of the current node in the tree.
        '''
        if self.is_leaf():
            return 1
        else:
            return 1 + sum(child.get_size() for child in self.children)

    def get_path(self) -> List[TreeNode]:
        '''
        Get the path from the root node to the current node.
        '''
        if self.is_root():
            return [self]
        else:
            return self.parent.get_path() + [self]

    def get_leaves(self) -> List[TreeNode]:
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

    def get_name(self) -> str:
        '''
        Get the name of the current node.
        '''
        res = '.'.join([str(n) for n in self.get_path()[:-1]])
        if res != '':
            res += '::'
        return res + str(self)

    def get_index_in_parent(self) -> Union[None, int]:
        '''
        Get the index of the current node in its parent's children list.
        '''
        if self.parent is None:
            return None
        else:
            return self.parent.children.index(self)

    def get_previous_sibling(self) -> Union[None, TreeNode]:
        '''
        Get the previous sibling of the current node.
        '''
        if self.parent is None:
            return None
        else:
            index = self.get_index_in_parent()
            if index == 0:
                return None
            else:
                return self.parent.children[index - 1]

    def get_next_sibling(self) -> Union[None, TreeNode]:
        '''
        Get the next sibling of the current node.
        '''
        if self.parent is None:
            return None
        else:
            index = self.get_index_in_parent()
            if index == len(self.parent.children) - 1:
                return None
            else:
                return self.parent.children[index + 1]

    def get_previous_tree_leaf_breadth_first(self) -> Union[None, TreeNode]:
        '''
        Get the previous leaf node int the root in breadth-first order.

        Works only on leaves.
        '''
        root = self.get_root()
        leaves = root.get_leaves()
        self_index = leaves.index(self)
        if self_index == 0:
            return None
        else:
            return leaves[self_index - 1]

    def get_next_tree_leaf_breadth_first(self) -> Union[None, TreeNode]:
        '''
        Get the next leaf node int the root in breadth-first order.
        Works only on leaves.
        '''
        root = self.get_root()
        leaves = root.get_leaves()
        self_index = leaves.index(self)
        if self_index == len(leaves) - 1:
            return None
        else:
            return leaves[self_index + 1]

    def get_path_to(self, other_node: TreeNode) -> List[Union[str, TreeNode]]:
        '''
        Get the path from the other_node to the current node.
        '''
        if self.get_root() != other_node.get_root():
            raise ValueError('Nodes are not in the same tree')

        this_path = self.get_path()
        other_path = other_node.get_path()

        common_prefix = []
        for i in range(min(len(this_path), len(other_path))):
            if this_path[i] != other_path[i]:
                break
            common_prefix.append(this_path[i])

        relative_path = []
        # Go up to the common prefix
        for i in range(len(this_path) - len(common_prefix)):
            relative_path.append('.' if i == 0 else '..')

        # Go down to the other node
        for i in range(len(common_prefix), len(other_path)):
            relative_path.append(other_path[i])

        return relative_path

    def to_string(self, prevprefix: str = '', position: str = 'first') -> str:
        if position not in ['first', 'middle', 'last']:
            raise ValueError('Invalid position')

        # Node representation
        prefix = ''
        if position == 'last':
            prefix += '└── '
        elif position == 'middle':
            prefix += '├── '

        result = prevprefix + prefix + str(self) + '\n'

        child_prevprefix = prevprefix
        if position == 'first':
            child_prevprefix += ''
        elif position == 'last':
            child_prevprefix += '    '
        elif position == 'middle':
            child_prevprefix += '│   '

        # Modify the prefix for child nodes │
        for i, child in enumerate(self.children):
            result += child.to_string(child_prevprefix,
                                      'last' if i == len(self.children) - 1 else 'middle')

        return result

    def prune(
            self,
            prune_condition: Callable[[TreeNode], bool] = lambda node: True,
            prune_again_after_children: bool = False) -> None:
        '''
        Prune the tree based on a prune condition.

        If prune_condition is no specified, the tree will be pruned by removing the
        whole subtree including the node itself.
        Otherwise, prune_condition has to be a function that takes a node as
        input and returns a boolean value. The node will be pruned if the function
        returns True. If the prune_condition is not met, the function will be
        called recursively on the children of the node.

        Note: when called on a root, it will behave like the prune_condition
        was False (will call prune on all children).

        If prune_again_after_children is True, the function will check condition again
        after the children removal. If the condition is met, the node will be
        pruned again. This can be really helpful when pruning a tree where all
        internal nodes should be pruned if they become leaves.
        '''
        if prune_condition(self) and not self.is_root():
            self.parent.remove_child(self)
        else:
            i = 0
            while i < len(self.children):
                old_ith_child = self.children[i]
                self.children[i].prune(
                    prune_condition, prune_again_after_children)
                # If the child was pruned, we don't want to increment i
                if i < len(
                        self.children) and old_ith_child == self.children[i]:
                    i += 1

            if prune_again_after_children and prune_condition(self):
                self.prune(prune_condition, prune_again_after_children=False)

    @abstractmethod
    def __str__(self) -> str:
        pass


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

    def __init__(self, root: Union[None, TreeNode] = None):
        '''
        Initialize a new Tree instance.
        '''
        self.root = TreeNode() if root is None else root

    def get_root(self) -> TreeNode:
        '''
        Get the root node of the tree.
        '''
        return self.root

    def is_root(self) -> bool:
        return True

    def get_parent(self) -> None:
        return None

    def set_parent(self, parent: TreeNode) -> None:
        self.get_rooot().set_parent(parent)
        self.root = parent

    def is_leaf(self) -> bool:
        return self.get_root().is_leaf()

    def add_child(self, child: TreeNode) -> None:
        return self.get_root().add_child(child)

    def get_children(self) -> List[TreeNode]:
        return self.get_root().get_children()

    def get_child(self, index: Union[int, TreeNode]) -> TreeNode:
        return self.get_root().get_child(index)

    def get_depth(self) -> int:
        return 0

    def get_height(self) -> int:
        return self.get_root().get_height()

    def get_size(self) -> int:
        return self.get_root().get_size()

    def get_path(self) -> List[TreeNode]:
        return [self.get_root()]

    def get_leaves(self) -> List[TreeNode]:
        return self.get_root().get_leaves()

    def to_string(self, prevprefix: str = '', position: str = 'first') -> str:
        return self.get_root().to_string(prevprefix, position)

    def prune(
            self,
            prune_condition: Callable[[TreeNode], bool] = lambda node: True,
            prune_again_after_children: bool = False) -> None:
        self.get_root().prune(prune_condition, prune_again_after_children)

    def __str__(self) -> str:
        return self.get_root().to_string()
