#!/usr/bin/env python

from btdtwf import configuration, connect
import os

testdir = os.path.dirname(__file__)
test_cfg_file = os.path.join(testdir, 'test_wf.cfg')

def test_parse():
    cfg = configuration.parse(test_cfg_file)
    wf = configuration.interpret(cfg)
    assert 3 == len(wf.input_nodes), str(wf.input_nodes)
    cfg = configuration.parse(test_cfg_file)
    wf = configuration.interpret(cfg, workflow='wf2')
    assert ['nodeD'] == wf.input_nodes, wf.input_nodes

def test_fail():
    cfg = configuration.parse(test_cfg_file)
    try:
        configuration.interpret(cfg , workflow = "doesnotexist")
    except configuration.NoSectionError:
        print 'Raised NoSectionError as expected'
    else:
        raise 'ValueError: should have raised NoSectionError'

def test_graph():
    cfg = configuration.parse(test_cfg_file)
    wf = configuration.interpret(cfg, workflow='wf2')
    g = configuration.make_graph(wf)

    for n1,n2,d in g.edges(data=True):
        print n1,n2,d
    connect(g)

    for n1,n2,d in g.edges(data=True):
        print n1,n2,d

    for name,nc in wf.nodes.items():
        print name, nc

    for node_name in wf.input_nodes:
        node = wf.nodes[node_name]
        node.object()


if '__main__' == __name__:
    test_parse()
    test_fail()
    test_graph()
