#!/usr/bin/env 

import networkx as nx
Graph = nx.DiGraph
import got, son, util


def connect(graph):
    for t,h,d in graph.edges(data=True):
        h.connect(t,**d)
    
