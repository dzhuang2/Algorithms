#!/usr/bin/python
# -------------------------------------------------------------------------------
# Name:        Fibonacci Heap
# Purpose:     Implement Fibonacci Heap in Python
#              For a detailed explanation of the algorithm,
#               see CLRS 3ed: Fibonacci Heap (Pg. 522)
# Author:      Di Zhuang
# Created:     08/24/2015
# Version:     1.0
# Copyright:   (c) Di Zhuang 2015
# -------------------------------------------------------------------------------

from scipy.constants import golden
from collections import deque
import numpy as np


def union(heap1, heap2):
    """
    Merges two Fibonacci heaps in O(1).
    Note: The previous two Fibonacci heaps are destroyed after merge operation

    :param heap1: Fibonacci heap #1
    :param heap2: Fibonacci heap #2
    :return: a Fibonacci heap with the two given heaps merged
    """
    assert isinstance(heap1, FibonacciHeap) and isinstance(heap2, FibonacciHeap), \
        "Both lists must be FibonacciHeaps"

    heap = FibonacciHeap()
    heap.merge(heap1)
    heap.merge(heap2)
    return heap


class Element(object):
    """
    Element is the internal data structure that holds the priority and object.

    self.obj: any object (e.g., a vertex or an edge for a graph algorithm)
    self.priority: priority of this node
    self.left, self.right: pointers to the siblings of this node
    self.parent: the parent of this node
    self.child: one of the children of this node
    self.degree: the degree of this node
    self.mark: whether this node has lost one of its children
    """

    def __init__(self, obj, priority):
        self.obj, self.priority = obj, priority
        self.left = self.right = self
        self.child = None
        self.parent = None
        self.degree = 0
        self.mark = False

    def get_value(self):
        """
        :return: object cached in this node
        """
        return self.obj

    def get_priority(self):
        """
        :return: priority of this node
        """
        return self.priority

    def children(self):
        """
        :return: all children of this node as a list
        """
        children = []
        x = self.child
        if x:
            while True:
                children.append(x)
                x = x.right
                if x == self.child:
                    break

        return children

    def siblings(self):
        """
        :return: all siblings of this node as a list
        """
        siblings = []
        x = self
        while True:
            siblings.append(x)
            x = x.right
            if x == self:
                break

        return siblings

    def __str__(self):
        # return "Element(obj={}, priority={})".format(self.obj, self.priority)  #  Fancier format
        return "({}, {})".format(self.obj, self.priority)


class FibonacciHeap(object):
    """
    Implements Fibonacci Heap
    """

    def __init__(self):
        """
        Creates an empty heap
        """
        self._size = 0
        self._min = None

    def insert(self, x, priority):
        """
        Insert a (x, priority) pair into the heap.
        Specifically, add the new node into the root list. If the priority
        of this node is the highest (lowest numerical value), update self._min_elem
        to reflect that.

        O(1) operation.

        :param x: obj associated with priority
        :param priority: priority of the object
        :return: an reference to the inserted node
        """

        elem = Element(x, priority)

        self._insert_to_root_list(elem)

        if self._min is None:  # if heap is empty
            self._min = elem
        elif self._min.priority > elem.priority:
            self._min = elem

        self._size += 1

        return elem

    def min(self):
        """
        :return: a reference to the minimal element in heap H
        """
        return self._min

    def extract_min(self):
        """
        Returns an reference to the minimal element in heap H and removes it from heap
        :return: an reference to element with the minimal priority value
        """
        z = self._min

        if z is not None:
            x = z.child

            if x is not None:
                # promote all children of the min to the root level
                while True:
                    next_child = x.right
                    x.parent = None
                    self._insert_to_root_list(x)
                    x = next_child
                    if x == z.child:
                        z.child = None
                        break

            if z == z.right:
                # if this is the only element in the heap, set self._min to None
                self._min = None
                self._remove_from_root_list(z)
            else:
                self._min = z.right
                self._remove_from_root_list(z)
                self._consolidate()

            self._size -= 1

        return z

    def decrease_key(self, x, new_priority):
        """
        Assigns to element x within heap H the new key value k,
        which is assumed to be less than or equal to its current key value

        :param x: an reference to the node in the heap
        :param new_priority: new priority of x
        :return:
        :raise: ValueError if the new priority is not strictly less than the old priority
        """
        if new_priority >= x.priority:
            raise ValueError("Decrease key: new priority value (%d) must "
                             "be less than old priority (%d)!"
                             % (new_priority, x.priority))

        x.priority = new_priority
        y = x.parent

        # if x is not at the root level, then cut x from the tree
        # and hang it in the root list
        if y is not None and x.priority < y.priority:
            self._cut(x, y)
            self._cascading_cut(y)

        # if x's new priority is less than the current minimal priority, change
        # the minimal of heap to x
        if x.priority < self._min.priority:
            self._min = x

    def delete(self, x):
        """
        Delete element x from heap. To maintain heap invariant, this operation
        is just 1 decrease key and 1 extract min operation.  Therefore,
        this takes O(log(n)) time.

        :param x: element to be deleted
        :return:
        """
        self.decrease_key(x, -np.inf)
        self.extract_min()

    def size(self):
        """
        :return: number of nodes in the heap
        """
        return self._size

    def merge(self, heap):
        """
        Merge this Fibonacci heap with another one.
        The time is O(1) since it just splices two circular doubly linked lists together.
        :param heap: another Fibonacci heap
        :return: None
        """
        assert isinstance(heap, FibonacciHeap), \
            "Invalid heap!"

        min_one = self._min
        min_two = heap.min()

        if min_one:
            min_one_right = self._min.right

            if min_two != min_two.right:  # if more than 1 root node in heap
                min_one.right, min_two.right.left, min_two.right, min_one_right.left = \
                    min_two.right, min_one, min_one_right, min_two
            else:
                self._insert_to_root_list(min_two)
        else:
            self._min = min_two

        self._size += heap.size()
        heap._clear()

    def __len__(self):
        """
        :return: number of nodes in the heap
        """
        return self.size()

    def _insert_to_root_list(self, elem):
        """
        Insert element into the root level of the Fibonacci heap

        :param elem: a reference to the elem to be inserted
        :return:
        """
        if elem.parent is not None:
            elem.parent = None

        if self._min:
            self._doublylinkedlist_insert(self._min, elem)
        else:
            self._min = elem

    @staticmethod
    def _doublylinkedlist_insert(head, y):
        """
        Given a node x in a circular doubly linked list, add y to the list.
        :param head: a node in a circular doubly linked list
        :param y: node to be inserted into the list
        :return:
        """
        if head is not None:
            tail = head.right
            tail.left, head.right, y.left, y.right = y, y, head, tail

    def _remove_from_root_list(self, z):
        """
        Remove a node from the root list in the Fibonacci heap.
        Note, z's children are untouched.

        :param z: a root level node
        :return: None
        """
        assert z.parent is None, \
            "Node should be at root level!"
        if z.right == z:
            self._min = None
        else:
            if z == self._min:
                # if the removed node is the minimal node, designate an arbitrary one to the be new min
                self._min = z.right
            z.left.right = z.right
            z.right.left = z.left
            z.left = z.right = z

    def _consolidate(self):
        """
        Perform an operation to enforce the forest rule, which means at the end of
        the consolidation, no two root trees can have the same degree.
        To accomplish this, this operation merges two trees of the same degree (d)
        into 1 tree with degree (d+1) similar to addition in binary.
        :return:
        """
        array = [None] * int(np.ceil(np.log(self._size)/np.log(golden))+1)

        # enqueue all the root nodes into a queue since their pointers will be overwritten
        # root list will be empty at the end of the loop
        q = deque()
        while self._min:
            q.append(self._min)
            self._remove_from_root_list(self._min)

        while len(q):
            x = q.popleft()
            d = x.degree

            while array[d] is not None:
                y = array[d]

                if x.priority > y.priority:
                    # this ensures that the node with the minimal priority will be the parent
                    x, y = y, x
                self._heap_link(y, x)
                array[d] = None
                d += 1
            array[d] = x

        # add all the new trees from the list back into the root list
        for elem in array:
            if elem is not None:
                if self._min is None:
                    self._min = elem
                else:
                    self._insert_to_root_list(elem)
                    if elem.priority < self._min.priority:
                        self._min = elem

    def _heap_link(self, y, x):
        """
        Link a node y to x, such that y become x's children
        :param y: y is to become the children of x
        :param x: x is to become the parent of y
        :return:
        """
        if x.child:
            self._doublylinkedlist_insert(x.child, y)
        else:
            x.child = y
        y.parent = x
        x.degree += 1
        y.mark = False

    def _cut(self, x, y):
        """
        Cut x from the list of children in y and hang it in the root list
        :param x: a child of y
        :param y: the parent of x
        :return:
        """
        # Note that y.child may not be x if y has more than 1 children
        assert x.parent == y, "Cut: nodes are not parent-child!"

        if x.right == x:  # x is the only child of y
            y.child = None
        else:  # remove x from the list of children of y
            y.child = x.right
            x.right.parent = y
            x.right.left = x.left
            x.left.right = x.right

        self._insert_to_root_list(x)
        y.degree -= 1  # decrement the degree of y since it has just lost a child

        # x.parent = None
        x.mark = False

    def _cascading_cut(self, y):
        """
        Cascading cut operation in Fibonacci Heap. If y is not at
        the root level or if y's parent has already lost one of its children (a.k.a, marked),
        recursively cut y's parent.
        :param y: a node in the heap
        :return:
        """
        z = y.parent
        if z is not None:
            if not y.mark:
                y.mark = True
            else:
                self._cut(y, z)
                self._cascading_cut(z)

    def _clear(self):
        """
        Empty the heap. Note, the nodes are NOT actually deleted from memory.
        As such, this can lead to memory leaks.  However, this should be called
        by the merge operation.
        :return:
        """
        self._min = None
        self._size = 0
