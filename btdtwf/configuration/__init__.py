#!/usr/bin/env python

import btdtwf
import ConfigParser
NoSectionError = ConfigParser.NoSectionError

def comma_list_split(string):
    if not string:
        return list()
    ret = [x.strip() for x in string.split(',')]
    return [x for x in ret if x]

def add_node_dict(nodes, cfg, name):
    if name in nodes.keys(): 
        return

    node_section_name = 'node %s'%name
    nodes[name] = dict(cfg.items(node_section_name), name=name)

    if not cfg.has_option(node_section_name, 'input_nodes'):
        return

    node_list = cfg.get(node_section_name, 'input_nodes')
    for node_name in comma_list_split(node_list):
        add_node_dict(nodes, cfg, node_name)

def parse(filename, **params):
    cfg = ConfigParser.SafeConfigParser()
    cfg.optionxform = str       # why would we want to lose case?
    cfg.read(filename)

    workflow = None
    workflows = []
    wfsectype = 'workflow '
    for sec in cfg.sections():
        if sec.startswith(wfsectype):
            workflows.append(sec[len(wfsectype):])

    if workflows:
        workflow = workflows[0]
    if cfg.has_section('defaults'):
        workflow = cfg.get('defaults','workflow')
    if params.has_key('workflow'):
        workflow = params.get('workflow')
    if not workflow in workflows:
        raise NoSectionError, 'No such workflow "%s" defined in %s' % (workflow, filename)

    params.update(dict(cfg.items('workflow %s' % workflow)))
    params['workflow'] = workflow

    nodes = dict()
    node_list = params.get('nodes')

    for node_name in comma_list_split(node_list):
        add_node_dict(nodes, cfg, node_name)
    params['nodes'] = nodes
    return params

def node_dict2node(nd):
    callable_name = nd['callable']
    mn, nc = callable_name.rsplit('.',1)
    importstr = 'from %s import %s' % (mn,nc)
    print importstr
    exec (importstr)
    node_ctor = eval(nc)
    return node_ctor(**nd)

def make_graph(workflow=None, nodes=None, **kwds):
    node_dicts = nodes or dict()
    graph = btdtwf.nx.Graph()

    # initial node addition
    node_objs = dict()
    for node_name, node_dict in node_dicts.items():
        node = node_dict2node(node_dict)
        node_objs[node_name] = node
        graph.add_node(node)
        
    # hook up edges
    for node_name, node_dict in node_dicts.items():
        this_node = node_objs[node_name]
        for onn in comma_list_split(node_dict.get('input_nodes')):
            other_node = node_objs[onn]
            graph.add_edge(other_node, this_node)

    return graph

        
        
    
