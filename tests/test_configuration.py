#!/usr/bin/env python

from btdtwf import configuration, connect
import os

testdir = os.path.dirname(__file__)
test_cfg_file = os.path.join(testdir, 'test_wf.cfg')

def test_parse():
    wf = configuration.parse(test_cfg_file)
    assert 3 == len(wf['nodes']), str(wf['nodes'].keys())
    wf = configuration.parse(test_cfg_file, workflow='wf2')
    assert ('nodeA','nodeB','nodeD') == tuple(wf['nodes'].keys()), str(wf['nodes'].keys())

def test_fail():
    try:
        configuration.parse(test_cfg_file, workflow = "doesnotexist")
    except configuration.NoSectionError:
        print 'Raised NoSectionError as expected'
    else:
        raise 'ValueError: should have raised NoSectionError'

def test_graph():
    wf = configuration.parse(test_cfg_file)
    g = configuration.make_graph(**wf)
    for n1,n2,d in g.edges(data=True):
        print n1,n2,d
    connect(g)

if '__main__' == __name__:
    test_parse()
    test_fail()
    test_graph()
