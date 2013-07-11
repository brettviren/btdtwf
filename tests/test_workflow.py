#!/usr/bin/env python 

import pyutilib.workflow as puwf

class TaskA(puwf.Task):
    def __init__(self, *args, **kwds):
        super(TaskA,self).__init__(*args, **kwds)
        self.inputs.declare('inout_x', default="default inout_x for "+self.name)
        self.inputs.declare('in_y', default="default in_y for "+self.name)
        self.outputs.declare('out_z', default="default out_z for "+self.name)
        #self.outputs.declare('inout_x', default="default out_x for "+self.name)

        print 'create TaskA "%s" id:%d' % (self.name, id(self))

    def execute(self):
        self.out_z = self.inout_x + self.in_y
        print 'EXECUTE TaskA "%s" id:%d execute: inout_x=%s in_y=%s out_z=%s' % \
            (self.name, id(self), self.inout_x, self.in_y, self.out_z)
        
if '__main__' == __name__:
    a = TaskA(name='a')
    b = TaskA(name='b')
    a.inputs.in_y = "fifty"
    #b.inputs.in_y = "forty"
    b.inputs.in_y = a.outputs.out_z
    b.inputs.inout_x = a.inputs.inout_x
    w = puwf.Workflow()
    w.add(a)
    print 'w()=',w()
    w = puwf.Workflow()
    w.add(a)
    print 'w(inout_x="one")',w(inout_x="one")
    w = puwf.Workflow()
    w.add(a)
    print 'w(inout_x="two")',w(inout_x="two")


