#!/usr/bin/python
# -------------------------------------------------------------------------------
# Name:        Skip List
# Purpose:     Implement Skip List in Python
#              For a detailed explanation of the algorithm,
#               see "A SkipList Cookbook" by William Pugh
#              (http://cglab.ca/~morin/teaching/5408/refs/p90b.pdf)
# Author:      Di Zhuang
# Created:     09/03/2015
# Version:     1.0
# Copyright:   (c) Di Zhuang 2015
# -------------------------------------------------------------------------------

from collections import deque
import numpy as np
# from Crypto.Random import random
import random


class Node(object):
    """
    Node is the internal data structure that key and value pair.

    self.key: any object (e.g., a vertex or an edge for a graph algorithm)
    self.value: priority of this node
    self.forward: a vector pointers to the next node
    """

    def __init__(self, key, value, level):
        self.key, self.value = key, value
        self.forward = [None] * level

    def key(self):
        """
        :return: key stored in the node
        """
        return self.key

    def value(self):
        """
        :return: value stored in the node
        """
        return self.value

    def __str__(self):
        """
        :return: string representation of this object
        """
        return "{}".format(self.key)

    def __repr__(self):
        """
        :return: string representation of this object that can be reconstructed with eval
        """
        return "Node({}, {})".format(self.key, self.value)


class SkipList(object):
    """
    Unlike the paper the levels are 0 indexed.

    MAX_LEVEL chosen for this implementation is 50, which means this data structure can
     contain up to 2^50 elements. In general, since MAX_LEVEL is the number of expected nodes
     at that level, the data structure expects on average (1/p)^MAX_LEVEL number of elements
    """
    MAX_LEVEL = 50

    def __init__(self):
        random.seed(43)  # for Debugging purposes
        self._size = 0
        self._head = Node(-np.inf, None)
        self._tail = Node(np.inf, None)
        self._level = 1

    def search(self, key):
        """
        Find the node with the given key
        :param key: search key
        :return: value associated with the searched key if found, None otherwise
        """
        x = self._head

        for i in xrange(self._level-1, -1, -1):
            while x.forward[i].key < key:
                x = x.forward[i]

        # move x from the last predecessor to next node on the last level
        x = x.forward[0]

        if x.key == key:
            return x.value
        else:
            return None

    def insert(self, key, val):
        update = self._update(key)
        x = update[0].forward[0]
        if x.key == key:
            x.value = val
        else:
            new_level = self._random_level()
            if new_level > self._level:
                for i in xrange(self._level+1, new_level+1):
                    update[i] = self._head
                self._level = new_level
            x = Node(key, val, new_level)
            for i in xrange(new_level+1):
                x.forward[i] = update[i].forward[i]
                update[i].forward[i] = x

    def delete(self, key):
        update = self._update(key)
        x = update[0].forward[0]
        if x.key == key:
            for i in xrange(self._level):
                if update[i].forward[i] != x:
                    break
                update[i].forward[i] = x.forward[i]
            while self._level and self._header.forward[self._level] == self._tail:
                self._level -= 1

    def _update(self, key):
        """
        Returns a vector of update so that when the search is complete,
        update[i] ocntains a pointer to the rightmost node of level i or
        higher that is to the left of the location of the insert or deletion.
        :param key: search key
        :return: a vector of nodes on each level such that each node is the closest predecessor
        """
        x = self._head
        update = [None] * self.MAX_LEVEL

        for i in xrange(self._level, 0, -1):
            while x.forward[i].key < key:
                x = x.forward[i]
            update[i] = x

        return update

    def _random_level(self, p=0.5):
        """
        Randomly determine the level of a node.  Flip a coin with probablity p that it
        is heads until it becomes tails.
        :return:
        """
        level = 0
        while random.random() < p and level < self.MAX_LEVEL:
            level += 1
        return level

    def __len__(self):
        """
        :return: number of nodes in the skip list
        """
        return self._size

    def size(self):
        """
        :return: number of nodes in the skip list
        """
        return len(self)

    def level(self):
        """
        :return: the highest level in the skip list
        """
        return self._level
