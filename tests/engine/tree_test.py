#!/usr/bin python3
# @File    : tree_test
# @Time    : 2020/3/11 11:29
# @Author  : Kelvin.Ye
from pymeter.engines.hashtree import HashTree
from pymeter.engines.traverser import HashTreeTraverser


class TestTraverser(HashTreeTraverser):
    def __init__(self):
        self.serial_number = 1

    def add_node(self, node, subtree) -> None:
        print(f'serial_number={self.serial_number}, node={node}')
        self.serial_number += 1

    def subtract_node(self) -> None:
        print('减节点')

    def process_path(self) -> None:
        print('到达子代末尾')


if __name__ == '__main__':
    third_level_tree_aa = HashTree()
    third_level_tree_aa.put('二级节点AA - 三级节点AA', HashTree())
    third_level_tree_aa.put('二级节点AA - 三级节点BB', HashTree())
    third_level_tree_aa.put('二级节点AA - 三级节点CC', HashTree())

    third_level_tree_bb = HashTree()
    third_level_tree_bb.put('二级节点BB - 三级节点AA', HashTree())
    third_level_tree_bb.put('二级节点BB - 三级节点BB', HashTree())
    third_level_tree_bb.put('二级节点BB - 三级节点CC', HashTree())

    second_level_tree = HashTree()
    second_level_tree.put('二级节点AA', third_level_tree_aa)
    second_level_tree.put('二级节点BB', third_level_tree_bb)

    first_level_tree = HashTree()
    first_level_tree.put('一级节点', second_level_tree)

    print(first_level_tree)

    observation_traversal = TestTraverser()
    first_level_tree.traverse(observation_traversal)
