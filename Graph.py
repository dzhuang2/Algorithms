#!/usr/bin/python
# -------------------------------------------------------------------------------
# Name:        UndirectedGraph
# Purpose:     Implement undirected graph in Python
#              Used to test the timings of Fibonacci heaps
# Author:      Di Zhuang
# Created:     08/24/2015
# Version:     1.0
# Copyright:   (c) Di Zhuang 2015
# -------------------------------------------------------------------------------

import random
import numpy as np
from FibonacciHeapTimed import FibonacciHeap, count
from time import time
import MinHeapTimed
from collections import defaultdict
import pickle
import sys


def timeit(fn):
    def decorator(*args, **kwargs):
        start = time()
        result = fn(*args, **kwargs)
        t = time() - start
        print '{} took {:0.5f} secs'.format(decorator.__name__, t)
        return result
    decorator.__name__ = fn.__name__
    decorator.called = 0
    decorator.avgtime = 0
    return decorator


class Vertex:
    def __init__(self, vid):
        self.id = vid
        self._neighbors = []
        self._edges = []

    def add_neighbor(self, neighbor):
        """
        Adds the neighbor node to this node's list of neighbors

        @input:
            neighbor: a Node object
        @output:
            None
        """
        self._neighbors.append(neighbor)

    def add_edge(self, edge):
        """
        Adds the neighbor node to this node's list of neighbors

        @input:
            neighbor: a Node object
        @output:
            None
        """
        assert edge.v_from == self.id or edge.v_to == self.id, \
            "one of the endpoints of this edge %s must be %d" % (edge, self.id)
        if edge.v_from == self.id:
            self.add_neighbor(edge.v_to)
        elif edge.v_to == self.id:
            self.add_neighbor(edge.v_from)

        self._edges.append(edge)

    def __str__(self):
        """
        __str__ (toString method for nodes)

        Mainly for debuggin purposes only, to invoke this function
        use str(Node)

        @input:
            None
        @output:
            a string detailing all of this node's neighbors
        """
        # return str(self.id) + ' neighbors: ' + ", ".join([str(v) for v in self._neighbors])
        return str(self.id)

    def __repr__(self):
        return self.__str__()

    def neighbors(self):
        """
        Returns a list of this node's neighbors

        @input:
            None
        @output:
            list of this node's neighbors
        """
        return self._neighbors

    def edges(self):
        """
        Returns a list of this node's neighbors

        @input:
            None
        @output:
            list of this node's neighbors
        """
        return self._edges


class Edge(object):
    def __init__(self, v_from, v_to, cap):
        self.cap = cap
        self.v_from = v_from
        self.v_to = v_to

    def capacity(self):
        return self.cap

    def __str__(self):
        return "(%s, %s)" % (self.v_from, self.v_to)


class UndirectedGraph:
    def __init__(self):
        self.vertices = {}

    def complete_graph(self, n, max_cap=100):
        for i in xrange(n):
            self.add_vertex(Vertex(i))

        for i in xrange(n):
            for j in xrange(i+1, n):
                self.add_edge(Edge(i, j, random.random()))

    def vertices(self):
        """
        Return a list of Nodes in this Graph
        """
        return self.vertices.keys()

    def add_vertex(self, vertex):
        """
        Insert the node into the graph
        """
        self.vertices[vertex.id] = vertex

    def vertex(self, vid):
        """
        Get a particular node using its id
        """
        try:
            return self.vertices[vid]
        except KeyError:
            print '{%s} not found in this undirected graph!' % vid

    def add_edge(self, edge):
        """
        addEdge(vid1, vid2)

        Adds edge between the two input Nodes.
        Internally, it adds Node1 to Node2's list of Neighbors
        and vice versa.
        """
        vid1 = edge.v_from
        vid2 = edge.v_to

        v1 = self.vertex(vid1)
        v2 = self.vertex(vid2)

        if v1 and v2:
            v1.add_edge(edge)
            v2.add_edge(edge)


def prims_fib(n, DEBUG=False):
    g = UndirectedGraph()
    g.complete_graph(n)
    heap = FibonacciHeap()

    mst = 0

    for i in xrange(n):
        heap.insert(g.vertex(i), np.inf)

    while len(heap):
        node = heap.extract_min()

        v, w = node.obj, node.priority

        if not np.isinf(w):
            mst += w

        for w, e in zip(v.neighbors(), v.edges()):
            cap = e.capacity()
            try:
                elem = heap[g.vertex(w)]
                if cap < elem.get_priority():
                    heap.decrease_key(elem, cap)
            except KeyError:
                pass

    if DEBUG:
        for fn in [heap.insert, heap.extract_min, heap.decrease_key, heap.__getitem__]:
            print '{}: called = {:d}, avg_time = {:0.5f}, total_time = {:0.5f}'.format\
                (fn.__name__, fn.called, fn.time / fn.called, fn.time)

    stats = {}
    for fn in [heap.insert, heap.extract_min, heap.decrease_key, heap.__getitem__]:
        stats[fn.__name__] = (fn.called, fn.time)

    return stats


def prims_minheap(n, DEBUG=False):
    g = init_graph(n)
    heap = MinHeapTimed.MinHeap()

    mst = 0

    for i in xrange(n):
        heap.push(MinHeapTimed.Element(g.vertex(i), np.inf))

    while len(heap):
        node = heap.pop()

        v, w = node.obj, node.priority

        if not np.isinf(w):
            mst += w

        for w, e in zip(v.neighbors(), v.edges()):
            cap = e.capacity()
            try:
                elem = heap[g.vertex(w)]
                if cap < elem.get_priority():
                    heap.decrease_key(elem, cap)
            except KeyError:
                pass

    if DEBUG:
        for fn in [heap.push, heap.pop, heap.decrease_key, heap.__getitem__]:
            print '{}: called = {:d}, avg_time = {:0.5f}, total_time = {:0.5f}'.format\
                (fn.__name__, fn.called, fn.time / fn.called, fn.time)

    stats = {}
    for fn in [heap.push, heap.pop, heap.decrease_key, heap.__getitem__]:
        stats[fn.__name__] = (fn.called, fn.time)

    return stats

@count
def init_graph(n):
    g = UndirectedGraph()
    g.complete_graph(n)
    return g


def print_results(filename):
    with open(filename, 'rb') as f:
        result = pickle.load(f)

    print 'Vertices\t\t\tFibonacci Heap\t\t\tMin Heap'
    names = ['']
    names.extend(sorted(result[0]['fibheap']))
    names.extend(sorted(result[0]['minheap']))
    print '\t'.join(names)

    for stat in result:
        print '{:05d}\t'.format(stat['vertices']),

        avg_times = []
        for fn in sorted(stat['fibheap']):
            called, total_time = [sum(x) for x in zip(*stat['fibheap'][fn])]
            fn_avg_time = float(total_time) / called
            avg_times.append(fn_avg_time)
        sys.stdout.write('\t'.join(['{:0.5f}'.format(val) for val in avg_times]))
        sys.stdout.write('\t')

        avg_times = []
        for fn in sorted(stat['minheap']):
            called, total_time = [sum(x) for x in zip(*stat['minheap'][fn])]
            fn_avg_time = float(total_time) / called
            avg_times.append(fn_avg_time)
        print '\t'.join(['{:0.5f}'.format(val) for val in avg_times])


def summarize(filename):
    with open(filename, 'rb') as f:
        result = pickle.load(f)

    print 'Vertices\t\t\tFibonacci Heap\t\t\tMin Heap'
    names = ['']
    names.extend(sorted(result[0]['fibheap']))
    names.extend(sorted(result[0]['minheap']))
    print '\tcalled\t'.join(names)

    for stat in result:
        print '{:05d}\t'.format(stat['vertices']),

        avg_times = []
        for fn in sorted(stat['fibheap']):
            called, total_time = [sum(x) for x in zip(*stat['fibheap'][fn])]
            avg_times.append(called)
            avg_times.append(total_time)
        sys.stdout.write('\t'.join(['{:0.5f}'.format(val) for val in avg_times]))
        sys.stdout.write('\t')

        avg_times = []
        for fn in sorted(stat['minheap']):
            called, total_time = [sum(x) for x in zip(*stat['minheap'][fn])]
            avg_times.append(called)
            avg_times.append(total_time)
        print '\t'.join(['{:0.5f}'.format(val) for val in avg_times])


def run_trials(trials=10, repeat=10):
    result = [None] * trials
    for i in xrange(trials):
        num = (i + 1) * 10
        result[i] = {}
        result[i]['vertices'] = num
        result[i]['fibheap'] = {}
        result[i]['minheap'] = {}

        for j in xrange(repeat):
            stats = prims_fib(num)
            for fn in stats:
                try:
                    result[i]['fibheap'][fn].append(stats[fn])
                except KeyError:
                    result[i]['fibheap'][fn] = [stats[fn]]

            stats = prims_minheap(num)
            for fn in stats:
                try:
                    result[i]['minheap'][fn].append(stats[fn])
                except KeyError:
                    result[i]['minheap'][fn] = [stats[fn]]

    with open('FibTrialResults.pickle', 'wb') as f:
        pickle.dump(result, f, pickle.HIGHEST_PROTOCOL)

    print_results('FibTrialResults.pickle')


if __name__ == '__main__':
    #  run_trials(3, 1)
    summarize('FibTrialResults.pickle')
