# SPDX-License-Identifier: MIT

import pytest
from docthing.tree import TreeNode, Tree

# A concrete implementation of the abstract TreeNode class for testing purposes


class MockTreeNode(TreeNode):
    def __str__(self):
        return "MockTreeNode()"

# Test TreeNode Initialization


def test_treenode_initialization():
    node = MockTreeNode()
    assert node.parent is None
    assert node.children == []

# Test is_root method


def test_is_root():
    node = MockTreeNode()
    assert node.is_root()

    child = MockTreeNode(parent=node)
    assert child.is_root() is False

# Test get_parent and set_parent methods


def test_parent_methods():
    parent = MockTreeNode()
    child = MockTreeNode()

    child.set_parent(parent)
    assert child.get_parent() == parent
    assert child.is_root() is False
    assert parent.is_root()

# Test is_leaf method


def test_is_leaf():
    parent = MockTreeNode()
    child = MockTreeNode()

    assert parent.is_leaf()  # No children
    parent.add_child(child)
    assert parent.is_leaf() is False
    assert child.is_leaf()  # Leaf since it has no children

# Test add_child and get_children


def test_add_and_get_children():
    parent = MockTreeNode()
    child1 = MockTreeNode()
    child2 = MockTreeNode()

    parent.add_child(child1)
    parent.add_child(child2)

    children = parent.get_children()
    assert len(children) == 2
    assert children[0] == child1
    assert children[1] == child2

# Test get_child by index


def test_get_child_by_index():
    parent = MockTreeNode()
    child1 = MockTreeNode()
    child2 = MockTreeNode()

    parent.add_child(child1)
    parent.add_child(child2)

    assert parent.get_child(0) == child1
    assert parent.get_child(1) == child2

    with pytest.raises(IndexError):
        parent.get_child(2)  # Out of bounds

# Test remove_child by index and node


def test_remove_child():
    parent = MockTreeNode()
    child1 = MockTreeNode()
    child2 = MockTreeNode()

    parent.add_child(child1)
    parent.add_child(child2)

    parent.remove_child(0)
    assert parent.get_children() == [child2]

    parent.remove_child(child2)
    assert parent.get_children() == []

    with pytest.raises(ValueError):
        parent.remove_child(child1)  # child1 already removed

# Test get_depth method


def test_get_depth():
    root = MockTreeNode()
    child = MockTreeNode()
    grandchild = MockTreeNode()

    root.add_child(child)
    child.add_child(grandchild)

    assert root.get_depth() == 0
    assert child.get_depth() == 1
    assert grandchild.get_depth() == 2

# Test get_height method


def test_get_height():
    root = MockTreeNode()
    child1 = MockTreeNode()
    child2 = MockTreeNode()
    grandchild = MockTreeNode()

    root.add_child(child1)
    root.add_child(child2)
    child1.add_child(grandchild)

    assert root.get_height() == 2  # root -> child1 -> grandchild
    assert child1.get_height() == 1
    assert child2.get_height() == 0  # child2 is a leaf
    assert grandchild.get_height() == 0  # grandchild is a leaf

# Test get_size method


def test_get_size():
    root = MockTreeNode()
    child1 = MockTreeNode()
    child2 = MockTreeNode()
    grandchild = MockTreeNode()

    root.add_child(child1)
    root.add_child(child2)
    child1.add_child(grandchild)

    assert root.get_size() == 4  # 1 (root) + 2 (children) + 1 (grandchild)
    assert child1.get_size() == 2  # 1 (child1) + 1 (grandchild)
    assert child2.get_size() == 1  # Only child2 itself

# Test get_path method


def test_get_path():
    root = MockTreeNode()
    child = MockTreeNode()
    grandchild = MockTreeNode()

    root.add_child(child)
    child.add_child(grandchild)

    assert root.get_path() == [root]
    assert child.get_path() == [root, child]
    assert grandchild.get_path() == [root, child, grandchild]

# Test get_leaves method


def test_get_leaves():
    root = MockTreeNode()
    child1 = MockTreeNode()
    child2 = MockTreeNode()
    grandchild = MockTreeNode()

    root.add_child(child1)
    root.add_child(child2)
    child1.add_child(grandchild)

    leaves = root.get_leaves()
    assert len(leaves) == 2
    assert grandchild in leaves
    assert child2 in leaves

# Test get_name method


def test_get_name_single_node():
    node = MockTreeNode()
    assert node.get_name() == "MockTreeNode()"


def test_get_name_path():
    root = MockTreeNode()
    child = MockTreeNode()
    grandchild = MockTreeNode()
    root.add_child(child)
    child.add_child(grandchild)

    assert root.get_name() == "MockTreeNode()"
    assert child.get_name() == "MockTreeNode()::MockTreeNode()"
    assert grandchild.get_name() == "MockTreeNode().MockTreeNode()::MockTreeNode()"

# Test relative path methods


def test_get_path_relative_to_same_node():
    node = MockTreeNode()
    assert node.get_path_to(node) == []


def test_get_path_relative_to_parent():
    parent = MockTreeNode()
    child = MockTreeNode()
    parent.add_child(child)
    assert child.get_path_to(parent) == ['.']


def test_get_path_relative_to_child():
    parent = MockTreeNode()
    child = MockTreeNode()
    parent.add_child(child)
    assert parent.get_path_to(child) == [child]


def test_get_path_relative_to_sibling():
    parent = MockTreeNode()
    child1 = MockTreeNode()
    child2 = MockTreeNode()
    parent.add_child(child1)
    parent.add_child(child2)
    assert child1.get_path_to(child2) == ['.', child2]


def test_get_path_relative_to_sibling_in_non_root():
    root = MockTreeNode()
    parent = MockTreeNode()
    child1 = MockTreeNode()
    child2 = MockTreeNode()
    root.add_child(parent)
    parent.add_child(child1)
    parent.add_child(child2)
    assert child1.get_path_to(child2) == ['.', child2]


def test_get_path_relative_to_distant_node():
    root = MockTreeNode()
    level1_1 = MockTreeNode()
    level1_2 = MockTreeNode()
    level2_1 = MockTreeNode()
    level2_2 = MockTreeNode()
    root.add_child(level1_1)
    root.add_child(level1_2)
    level1_1.add_child(level2_1)
    level1_2.add_child(level2_2)

    assert level2_1.get_path_to(level2_2) == ['.', '..', level1_2, level2_2]


def test_get_path_relative_to_different_trees():
    tree1 = MockTreeNode()
    tree2 = MockTreeNode()

    with pytest.raises(ValueError, match='Nodes are not in the same tree'):
        tree1.get_path_to(tree2)


def test_prune_leaf_node():
    root = MockTreeNode()
    child = MockTreeNode()
    root.add_child(child)

    child.prune()
    assert len(root.children) == 0


def test_prune_subtree():
    root = MockTreeNode()
    child1 = MockTreeNode()
    child2 = MockTreeNode()
    grandchild = MockTreeNode()
    root.add_child(child1)
    root.add_child(child2)
    child1.add_child(grandchild)

    child1.prune()
    assert len(root.children) == 1
    assert root.get_size() == 2


def test_prune_with_condition():
    root = MockTreeNode()
    child1 = MockTreeNode()
    child2 = MockTreeNode()
    grandchild1 = MockTreeNode()
    grandchild2 = MockTreeNode()
    root.add_child(child1)
    root.add_child(child2)
    child1.add_child(grandchild1)
    child1.add_child(grandchild2)

    root.prune(lambda node: node.get_depth() % 2 == 0)
    assert len(root.children) == 2
    assert len(child1.children) == 0
    assert len(child2.children) == 0


def test_prune_root():
    root = MockTreeNode()
    child = MockTreeNode()
    root.add_child(child)

    root.prune()
    assert root.is_leaf()


def test_prune_empty_tree():
    root = MockTreeNode()
    root.prune(lambda node: False)
    assert root.is_leaf()


def test_prune_all_nodes():
    root = MockTreeNode()
    child1 = MockTreeNode()
    child2 = MockTreeNode()
    root.add_child(child1)
    root.add_child(child2)

    root.prune(lambda node: True)
    assert root.is_leaf()


def test_prune_connections():
    root = MockTreeNode()
    child1 = MockTreeNode()
    child2 = MockTreeNode()
    root.add_child(child1)
    root.add_child(child2)

    child1.prune()
    child2.prune()
    assert len(root.children) == 0
    assert child1.parent is None
    assert child2.parent is None

# Test Tree class


def test_tree_class():
    root = MockTreeNode()
    tree = Tree(root=root)

    assert tree.get_root() == root
    assert tree.is_root()
    assert tree.get_depth() == 0
    assert tree.get_height() == 0  # No children yet
    assert tree.get_size() == 1  # Only root
    assert tree.get_path() == [root]
