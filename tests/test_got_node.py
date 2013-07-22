#!/usr/bin/env python
'''
Test son.nodes.GotNode
'''

import tempfile
import btdtwf

workdir = tempfile.mkdtemp(prefix='test_got_node_')

def setup_func():
    print 'Using workdir:',workdir

def teardown_func():
    print 'Not removing',workdir
    

def save_inputs(conns, **kwds):
    import json
    filename = kwds['filename']
    with open(filename, 'w') as fp:
        vals = {c():v for c,v in conns.items()}
        tosave = dict(vals=vals, kwds=kwds)
        fp.write(json.dumps(tosave, indent=2))
    return filename
        

def test_got_node():
    
    got = btdtwf.got.Got(workdir)

    gen_node = btdtwf.son.nodes.CallableNode(save_inputs, filename = 'test_got_node.json')
    got_node = btdtwf.son.nodes.GotNode(got, 'start', 'Initial test', 'test1')
    
    graph = btdtwf.Graph()
    graph.add_edge(gen_node, got_node)
    btdtwf.connect(graph)

    ret = got_node()
    print 'test_got_node returns:',ret



if __name__ == '__main__':
    setup_func()

    test_got_node()

    teardown_func()
