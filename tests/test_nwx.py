#!/usr/bin/env python
'''
Test networkx
'''
import networkx as nx

class MyEdge(object):
    def __init__(self, a, b):
        self.a, self.b = a,b
        self._cache = None
    def __call__(self):
        if self._cache is None:
            self._cache = self.a()
        return self._cache
    def __str__(self):
        if self._cache is None:
            return '%s --> %s' % (self.a, self.b)
        return '%s ==> %s' % (self.a, self.b)
    def __repr__(self):
        return '<edge> %s' % str(self)
        

class MyNode(object):
    def __init__(self, value = None):
        self._value = value

    def __call__(self):
        return self._value

    def __str__(self):
        return str(self._value)
    def __repr__(self):
        return "%s %s" % (type(self._value), self._value)

class MyDiGraph(nx.DiGraph):

    def add_edge(self, a,b, *args, **kwds):
        if not isinstance(a, MyNode): a = MyNode(a)
        if not isinstance(b, MyNode): b = MyNode(b)
        e = MyEdge(a,b)
        super(MyDiGraph,self).add_edge(a,b, *args, object=e, **kwds)
        return
        
def make_test_graph():
    G = MyDiGraph()

    G.add_edge(10,21)
    G.add_edge(21,22)
    G.add_edge(22,23)

    G.add_edge(23,24)

    G.add_edge(10,31)
    G.add_edge(31,32)
    G.add_edge(32,33)
    G.add_edge(33,34)
    return G

