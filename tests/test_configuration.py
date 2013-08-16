#!/usr/bin/env python

from btdtwf import configuration, connect, main
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

def test_params():
    cfg = configuration.parse(test_cfg_file)
    wf = configuration.interpret(cfg, workflow='wf1')
    assert wf.params.workflow == 'wf1'
    assert wf.params.par3 == wf.params.format('{par1} {par2}') # this needs to match what is in test_wf.cfg
    print 'Params:', wf.params
    assert wf.workdir == 'run-wf1', wf.workdir

def test_get_workflow_name():
    cfg = configuration.parse(test_cfg_file)
    for wfname in ['wf1', 'wf2', '', None]:
        wf = configuration.interpret(cfg, workflow=wfname)
        assert wf.name, (wfname, wf.name)
        if wfname:
            assert wfname == wf.name, (wfname, wf.name)
    

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

def test_run():
    cfg = configuration.parse(test_cfg_file)
    wf = configuration.interpret(cfg, workflow='wf1')
    result = configuration.run(wf)
    print result

def test_main():
    for wf in ['wf1', 'wf2']:
        cmdline = '-w %s %s' % (wf, test_cfg_file)
        r = main(cmdline.split())
        assert r, str(r)
        


if '__main__' == __name__:
    test_parse()
    test_fail()
    test_params()
    test_get_workflow_name()
    test_graph()
    test_run()
    test_main()
