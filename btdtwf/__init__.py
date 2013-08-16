#!/usr/bin/env 

import networkx as nx
Graph = nx.DiGraph
import got, son, util


def connect(graph):
    for t,h,d in graph.edges(data=True):
        h.connect(t,**d)

from btdtwf import configuration
import argparse


def main(args):
    parser = argparse.ArgumentParser(description='Run Cowbells Workflow')
    parser.add_argument('-w','--workflow', help='Name of workflow to use')
    parser.add_argument('config', nargs='+', help='Configuration file')
    opts = parser.parse_args(args)
    cfg = configuration.parse(opts.config)
    wf = configuration.interpret(cfg, workflow= opts.workflow)
    return configuration.run(wf)


    
