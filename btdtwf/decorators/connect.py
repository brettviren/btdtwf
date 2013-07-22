#!/usr/bin/env python
'''
Decorators for a nodes connect() method.

'''

from collections import namedtuple

def connect_named_tuple(name='connection'):
    '''Convert (node, **kwds) to a named tuple.  

    The node is accessible from .node (clobbering any "name" key in
    <kwds>).  The tuple will be named by the decorators <name>
    argument if there is not "name" key found in the <kwds>.

    '''
    def wrapper(f_connect):
        def wrap(node, **kwds):
            ntname = kwds.get('name',name)
            kwds['node'] = node
            nt = namedtuple(ntname, kwds.keys())(**kwds)
            f_connect(nt)
        return wrap
    return wrapper


            
