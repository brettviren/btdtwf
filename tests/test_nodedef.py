#!/usr/bin/envy python
'''Want a way to express a layer of functionality:

 - named edge connections translated to calling callable like callable(**kwds)

 - call .format() any string values in **kwds with the other kwds of
   string value until all satisfied

 - persistent store of output indexed by input

 - use store as cache if result exists

 - interpret specially marked input as input file names to check for
   outdated files

'''


from collections import OrderedDict

class CallableNode:
    def __init__(self, callable):
        self._callable = callable
        self._input = OrderedDict()
        self._cache = None

    def connect(self, node, **kwds):
        self._input[node] = kwds

    def __call__(self):
        if self._cache != None:
            return self._cache

        args = OrderedDict({n():d for n,d in self._input.items()})
        self._cache = self._callable(args)
        return self._cache



def chirp(args):
    print '%d args: %s' % (len(args), str(args))
    return args.get('number', -1)

def test_cn():
    import networkx as nx
    G = nx.DiGraph()
    
    nodes = [CallableNode(chirp) for x in range(4)]
    for count, (n1,n2) in enumerate(zip(nodes[:-1], nodes[1:])):
        G.add_edge(n1,n2, number=count)

    for t,h,d in G.edges(data=True):
        h.connect(t,**d)

    nodes[-1]()

    return G
            

    

if '__main__' == __name__:
    test_cn()
