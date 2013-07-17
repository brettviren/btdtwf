#!/usr/bin/env python

import networkx as nx


class NamedNode(object):
    def __init__(self, name, *args, **kwds):
        self._name = name
        self.inputs = []
        self.input = None

    def connect(self, node, **kwds):
        print self._name,'connect',node,kwds
        self.inputs.append((node,kwds))

    def __call__(self):
        return self._name

    def __str__(self):
        return '<NamedNode "%s">' % self._name

    def __repr__(self):
        return str(self)

class FuncNode():
    def __init__(self, **defaults):
        self._params = {k:lambda:v for k,v in defaults.items()}
    def connect(self, node, name=None, **other):
        if name is None:
            raise KeyError, 'Need name'
        self._params[name] = node
    def __call__(self):
        return {k:v() for k,v in self._params.items()}


class ScalarFromDict:
    def __init__(self, name):
        self._name = name
        self._node = None
    def connect(self, node, **other):
        self._node = node
    def __call__(self):
        return self._node()[self._name]

class Chirp:
    def __init__(self, node):
        self._node = node
    def __call__(self):
        print 'Calling:', self._node
        val = self._node()
        print 'Got:',val
        return val
    def connect(self, node, **kwds):
        self._node.connect(node, **kwds)

def make_some():
    G = nx.DiGraph()
    a,b,c = [NamedNode(x) for x in ('a','b','c')]

    G.add_edge(a,b, name='x')
    G.add_edge(b,c, name='y')
    G.add_edge(a,c, name='z')

    fn = FuncNode(a=1,b=2,c=3,d=4)
    G.add_edge(a,fn,name='a')
    G.add_edge(b,fn,name='b')
    G.add_edge(c,fn,name='c')

    sfd = ScalarFromDict('d')
    G.add_edge(fn,sfd)

    for t,h,d in G.edges(data=True):
        h.connect(Chirp(t),**d)
    return G

