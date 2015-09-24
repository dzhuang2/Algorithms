#!/usr/bin/python
# -------------------------------------------------------------------------------
# Name:        MinHeap
# Purpose:     Implement MinHeap in Python
#              Modified as a class and include a decrease key operation
# Author:      Di Zhuang
# Created:     09/11/2015
# Version:     1.0
# Copyright:   (c) Di Zhuang 2015
# -------------------------------------------------------------------------------

import random
from FibonacciHeapTimed import count


class Element(object):
    """
    Element is the internal data structure that holds the priority and object.

    self.obj: any object (e.g., a vertex or an edge for a graph algorithm)
    self.priority: priority of this node
    """

    def __init__(self, obj, priority):
        self.obj, self.priority = obj, priority

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

    def __repr__(self):
        return str(self)

    def __str__(self):
        # return "Element(obj={}, priority={})".format(self.obj, self.priority)  #  Fancier format
        return "({}, {})".format(self.obj, self.priority)

    def __lt__(self, other):
        return self.priority < other.priority


class MinHeap(object):
    def __init__(self):
        self._heap = []
        self._dict = {}  # keeps track of the the position of each item

    @count
    def push(self, item):
        """Push item onto heap, maintaining the heap invariant."""
        assert isinstance(item, Element), \
            "Push: Invalid element!"
        self._dict[item.obj] = len(self._heap)
        self._heap.append(item)
        self._bubble_up(len(self._heap)-1)

    @count
    def pop(self):
        """Pop the smallest item off the heap, maintaining the heap invariant."""
        if len(self._heap):
            self._swap(0, len(self._heap)-1)
            min_item = self._heap.pop()
            del self._dict[min_item.obj]

            if len(self._heap):
                self._bubble_down(0)

            return min_item
        else:
            raise IndexError("Pop: Heap is empty!")

    @count
    def decrease_key(self, item, new_priority):
        """Pop the smallest item off the heap, maintaining the heap invariant."""
        if new_priority > item.priority:
            raise ValueError("Decrease key: new priority value (%s) must "
                             "be less than old priority (%s)!"
                             % (new_priority, item.priority))

        item.priority = new_priority
        self._bubble_up(self._dict[item.obj])

    def _swap(self, i, j):
        self._dict[self._heap[i].obj] = j
        self._dict[self._heap[j].obj] = i
        self._heap[i], self._heap[j] = self._heap[j], self._heap[i]

    def _bubble_down(self, index):
        while index < len(self._heap):
            left_child_index = index * 2 + 1
            right_child_index = left_child_index + 1
            min_index = index

            if left_child_index < len(self._heap) \
                    and self._heap[left_child_index] < self._heap[min_index]:
                min_index = left_child_index

            if right_child_index < len(self._heap) \
                    and self._heap[right_child_index] < self._heap[min_index]:
                min_index = right_child_index

            if min_index == index:  # current elem is smaller than both children
                return
            else:   # swap current elem with the smaller of the two children
                self._swap(min_index, index)
                index = min_index

    def _bubble_up(self, index):
        while index > 0:
            parent_index = (index - 1) // 2
            if self._heap[index] < self._heap[parent_index]:
                self._swap(index, parent_index)
                index = parent_index
                continue
            return

    def __len__(self):
        return len(self._heap)

    @count
    def __getitem__(self, item):
        try:
            return self._heap[self._dict[item]]
        except KeyError:
            raise KeyError("Object %s no longer in heap!" % item)


def test_decrease_key(n):
    '''Test decrease_key method'''
    heap = MinHeap()

    ls_elems = []

    expected_list = []
    for i in xrange(n):
        priority = random.random()
        item = Element(i, priority)
        ls_elems.append(item)
        heap.push(item)
        expected_list.append((i, priority))

    random_indices = range(n)
    random.shuffle(random_indices)

    for i in random_indices[:n//2]:
        item = ls_elems[i]
        new_priority = item.priority - random.random()
        expected_list[i] = (item.obj, new_priority)
        heap.decrease_key(item, new_priority)

    expected_list.sort(key=lambda x: x[1])

    actual_list = []
    while len(heap):
        item = heap.pop()
        actual_list.append((item.obj, item.priority))

    if actual_list == expected_list:
        print 'test_decrease_key: working!'
    else:
        print 'test_decrease_key: actual_list != expected_list'
        return False


def test_sort(n):
    heap = MinHeap()

    correct_result = []
    for i in xrange(n):
        priority = random.randint(0, 100) + random.random()
        correct_result.append((i, priority))
        heap.push(Element(i, priority))

    correct_result.sort(key=lambda x: x[1])

    test_result = []
    while len(heap):
        item = heap.pop()
        test_result.append((item.obj, item.priority))

    if test_result == correct_result:
        print "It works!"
    else:
        print "Something is wrong!"


if __name__ == '__main__':
    test_sort(1000)
    test_decrease_key(1000)
