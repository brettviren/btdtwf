#!/usr/bin/env python 

import pyutilib.workflow as puwf

class TaskA(puwf.Task):
    def __init__(self, *args, **kwds):
        super(TaskA,self).__init__(*args, **kwds)
        self.inputs.declare('globalvar', default="")
        self.inputs.declare('in_x', default=10)
        self.inputs.declare('in_y', default=20)
        self.outputs.declare('out_z', default=30)

        print 'create TaskA "%s" id:%d' % (self.name, id(self))

    def execute(self):
        self.out_z = self.in_x + self.in_y
        print 'EXECUTE TaskA "%s" id:%d execute: in_x=%s in_y=%s out_z=%s, globalvar=%s' % \
            (self.name, id(self), self.in_x, self.in_y, self.out_z, self.globalvar)
        
if '__main__' == __name__:
    defaults = dict(globalvar='some global variable')

    #w = puwf.Workflow()

    b = TaskA(name='TaskA2')
    a = TaskA(name='TaskA1')
    a.inputs.in_x = 1
    b.inputs.in_x = 2
    b.inputs.in_y = a.outputs.out_z

    print 'workflow'
    w = puwf.Workflow()
    w.add(a)
    res = w(in_y=100, **defaults)
    print 'w()=',res


