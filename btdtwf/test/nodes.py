#!/usr/bin/env python

from btdtwf.son.nodes import BaseNode

class TestCallable(BaseNode):
    def run(self):
        print 'Calling', self._node_kwds.get('name', 'TestCallable')
        return None
