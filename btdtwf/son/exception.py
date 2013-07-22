#!/usr/bin/env python

class NodeError(Exception):
    def __init__(self, msg, node, **kwds):
        self.msg,self.node.self.kwds = msg,node,kwds
    def __str__(self):
        return '%s (node="%s")' % (self.msg, self.node)

class CallError(NodeError): pass
class ConnectError(NodeError): pass

