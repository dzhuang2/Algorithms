# Algorithms
Investigating various classic data structures and algorithms

Motivation:
Examine classic advanced data structures to gain a deeper insight into their implementation challenges and real costs. Often times, complexity analysis stops at the big O notation.  While big O notation is convenient to assess the performance of certain operations asymptotically, some of the large constants hidden in these big Os hides the trade off between algorithm complexity and operation cost.  I subsribe to Knuth's method of analyzing algorithms by first get a good implementation of the algorithm / data structure, and then profile the operations to investigate how big these big O constants look like and perform basic regression analysis to see at what scale does the advanced data structures outperforms its simpler counterpart.

First of these basic data structures I investigated is the Fibonacci heap, well known for having a large big O constant (due to its lazyness). For this, I have implemented it in Python, the source code of which is contained in FibonacciHeap.py.  To compare the heap, I also implemented the MinHeap (min priority heap). Timing is based on Prim's algorithm and test results is performed on complete graphs. FibonacciDraw(requires Pyqt) offers a graphic representation of the operations offered in Fibonacci heaps.
