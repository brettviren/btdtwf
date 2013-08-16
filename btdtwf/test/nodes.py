#!/usr/bin/env python

from btdtwf.son.nodes import BaseNode

class TestCallable(BaseNode):
    instance_count = 0

    def run(self):
        TestCallable.instance_count += 1
        name = self._node_kwds.get('name', 'TestCallable')
        print 'Calling', name, self.instance_count
        return '%s%d' % (name, self.instance_count)
