#!/usr/bin/env python

import os
from collections import namedtuple
from btdtwf import Graph
from btdtwf.util import format_flat_dict, cd
import ConfigParser
NoSectionError = ConfigParser.NoSectionError
NoOptionError = ConfigParser.NoOptionError

WorkflowConfig = namedtuple('WorkflowConfig','name nodes input_nodes params workdir')
NodeConfig = namedtuple('NodeConfig', 'name object input_nodes ctor kwdargs')

def comma_list_split(string):
    if not string:
        return list()
    ret = [x.strip() for x in string.split(',')]
    return [x for x in ret if x]

def parse(filename):
    'Return a configuration object made by parsing filename (or list of filenames)'
    cfg = ConfigParser.SafeConfigParser()
    cfg.optionxform = str       # why would we want to lose case?
    cfg.read(filename)
    return cfg


def make_node_object(ctor, **kwds):
    print 'Making node constructor: "%s"' % ctor
    mn, nc = ctor.rsplit('.',1)
    importstr = 'from %s import %s' % (mn,nc)
    exec (importstr)
    node_ctor = eval(nc)
    obj = node_ctor(**kwds)
    if not obj:
        raise ValueError, 'No node object returned from %s(%s)' % \
            (ctor, ', '.join(['%s=%s'%kv for kv in kwds.items()]))
    return obj


def add_node_dict(nodes, cfg, name, **kwds):
    if name in nodes.keys(): 
        return                  # already got it

    node_section_name = 'node %s'%name
    nsecdict = dict(cfg.items(node_section_name))

    try:
        input_nodes = nsecdict.pop('input_nodes')
    except KeyError:
        input_nodes = []
    else:
        input_nodes = comma_list_split(input_nodes)
        for dep_name in input_nodes:
            add_node_dict(nodes, cfg, dep_name, **kwds)

    ctor = nsecdict.pop('constructor') # required node section item
    nsecdict.setdefault('node_name', name)
    ctor_kwds = format_flat_dict(nsecdict, **kwds)
    all_kwds = dict(kwds, **ctor_kwds)
    obj = make_node_object(ctor, **all_kwds)
    nodes[name] = NodeConfig(name=name, object=obj, input_nodes=input_nodes, ctor=ctor, kwdargs=all_kwds)


def get_workflow_name(cfg, override=None):
    'Return the requested workflow name, raise NoSectionError if not found in the configuration object'
    workflows = []
    for sec in cfg.sections():
        if sec.startswith('workflow '):
            workflows.append(sec[len('workflow '):])
    workflow = None
    if workflows:               # default is first one in file
        workflow = workflows[0]
    if cfg.has_section('defaults'): # unless a defaults section gives it
        workflow = cfg.get('defaults','workflow')
    if override:                # and unless caller doesn't override
        workflow = override
    if not workflow in workflows: # regardless, gotta have a matching section
        raise NoSectionError, 'No such workflow "%s" defined (have: %s)' % (workflow, ', '.join(workflows))
    return workflow

def get_params(cfg, params_name):
    'Return a dictionary of parameters section values'
    try:
        parameters = cfg.items('parameters %s' % params_name)
    except NoSectionError:
        return dict()
    p = dict(parameters)
    try:
        more = p.pop('parameters')
    except KeyError:
        return p
    # coalesce daughters before updating mother
    more_p = dict()
    for sp in comma_list_split(more):
        more_p.update(get_params(cfg, sp))
    p.update(more_p)
    return p

def get_workflow_params(cfg, workflow):
    'Return a flattened and formatted dictionary of the workflow parameters'
    ret = dict()
    try:
        plist = cfg.get('workflow '+workflow, 'parameters')
    except NoOptionError:
        return ret

    for psec in comma_list_split(plist):
        ret.update(get_params(cfg, psec))
    return ret

def get_workflow_nodes(cfg, workflow, **kwds):
    input_nodes = cfg.get('workflow '+workflow, 'input_nodes') # required node section item
    ret = dict()
    for nname in comma_list_split(input_nodes):
        add_node_dict(ret, cfg, nname, **kwds)
    return ret

def make_params(**params):
    class Params(namedtuple('Params', params.keys())):
        def format(self, string, **extra):
            d = dict(params, **extra)
            return string.format(**d)
    return Params(**params)

def get_workflow_directory(cfg, workflow, **kwds):
    try:
        wd = cfg.get('workflow ' + workflow, 'directory')
    except NoOptionError:
        wd = '.'
    return wd.format(workflow=workflow, **kwds)

    

def interpret(cfg, **extra_params):
    workflow_name = get_workflow_name(cfg, extra_params.get('workflow'))
    params = get_workflow_params(cfg, workflow_name)
    params['workflow'] = workflow_name
    params_ff = format_flat_dict(params, **extra_params)
    params_nt = make_params(**params_ff)
    all_params = dict(extra_params, **params_ff)
    workdir = get_workflow_directory(cfg, **all_params)

    input_node_names = cfg.get('workflow '+workflow_name, 'input_nodes') # required node section item
    input_node_names = input_node_names.format(**all_params)
    input_node_names = comma_list_split(input_node_names)

    nodes = dict()
    for nname in input_node_names:
        add_node_dict(nodes, cfg, nname, **all_params)

    return WorkflowConfig(name=workflow_name, 
                          nodes = nodes, 
                          input_nodes=input_node_names,
                          params = params_nt, 
                          workdir = workdir)



def make_graph(wf):
    graph = Graph()

    # initial node addition
    for node in wf.nodes.values():
        graph.add_node(node.object)
        
    # hook up edges
    for node in wf.nodes.values():
        for node_name in node.input_nodes:
            other_node = wf.nodes[node_name]
            graph.add_edge(other_node.object, node.object, node_name = node_name)

    return graph

        
        
    
def run(wf):
    print 'Running workflow %s in %s' % (wf.name, wf.workdir)
    with cd(wf.workdir, mkdir=True):
        g = make_graph(wf)
        for t,h,d in g.edges(data=True):
            h.connect(t,**d)
        ret = list()
        for node_name in wf.input_nodes:
            node = wf.nodes[node_name]
            r = node.object()
            ret.append(r)
        return ret

    
import argparse
def main(args):
    parser = argparse.ArgumentParser(description='Run Cowbells Workflow')
    parser.add_argument('-w','--workflow', help='Name of workflow to use')
    parser.add_argument('config', nargs='+', help='Configuration file')
    opts = parser.parse_args(args)

    config_files = map(os.path.realpath, opts.config)
    cfg = parse(config_files)
    wf = interpret(cfg, workflow= opts.workflow, __config_files__ = ','.join(config_files))
    result = run(wf)
    print result
    return result
