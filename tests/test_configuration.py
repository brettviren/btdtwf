#!/usr/bin/env python

from btdtwf import configuration, connect
import os

testdir = os.path.dirname(__file__)
test_cfg_file = os.path.join(testdir, 'test_wf.cfg')

def test_parse():
    wf = configuration.parse(test_cfg_file)
    assert 3 == len(wf['nodes']), str(wf['nodes'].keys())
    wf = configuration.parse(test_cfg_file, workflow='wf2')
    assert set(['nodeD']) == set(wf['input_nodes']), str(wf['input_nodes'])

def test_fail():
    try:
        configuration.parse(test_cfg_file, workflow = "doesnotexist")
    except configuration.NoSectionError:
        print 'Raised NoSectionError as expected'
    else:
        raise 'ValueError: should have raised NoSectionError'

def test_graph():
    wf = configuration.parse(test_cfg_file, workflow='wf2')
    g = configuration.make_graph(**wf)
    for n1,n2,d in g.edges(data=True):
        print n1,n2,d
    connect(g)

    for n1,n2,d in g.edges(data=True):
        print n1,n2,d

    for name,node in wf['nodes'].items():
        print name,node

    for node_name in wf['input_nodes']:
        node = wf['nodes'][node_name]
        node['object']()


if '__main__' == __name__:
    test_parse()
    test_fail()
    test_graph()
