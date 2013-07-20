#!/usr/bin/env python
'''
Functional network workflow.
'''






class ParamNode(object):
    def __init__(self, default = None, setme = None):
        self.value = default
        self._setme = setme
        self._connected = None

    def __call__(self):
        if self._connected:
            return self._connected()
        if self._setme:
            self._setme()
        return self.value

    def connect(self, other):
        self._connected = other

class FedNode(object):
    def __init__(self, feeder):
        self._feeder = feeder
        self._cache = None
    def __call__(self):
        if self._cache is None:
            self._cache = self._feeder(self)
        return self._cache

class FuncNode(object):
    def __init__(self, inputs = None):
        self._cache = None
        self.inputs = inputs or set()

    def __call__(self):
        if self._cache is None:
            self._cache = self.run()
        return self._cache

    def run(self):
        return None

class MultiFuncNode(FuncNode):
    def __init__(self, inputs = None, outputs = None):
        super(MultiFuncNode,self).__init__(inputs)
        self.outputs = [ParamNode(default=x, setme = self) for x in outputs or list()]

    # subclass implements run() and sets each [x.value for x in self.outputs]

class SumNode(FuncNode):
    def run(self):
        return reduce(lambda x,y:x+y, [x() for x in self.inputs])

class StaticNode(object):
    def __init__(self, value):
        self._value = value
    def __call__(self):
        return self._value

one = StaticNode("one")
two = StaticNode("two")
pn = ParamNode("three")
s = SumNode(inputs = [one, pn])
print s()
pn.connect(two)
s = SumNode(inputs = [one, pn])
print s()
one = StaticNode(1)
two = StaticNode(2)
s = SumNode(inputs = [one, two, lambda:3])
print s()
