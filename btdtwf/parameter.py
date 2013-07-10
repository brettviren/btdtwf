#!/usr/bin/env python
'''
A parameter is a named and typed quantity which caries serialization functions.
'''

from collections import namedtuple, OrderedDict
import pickle

Parameter = namedtuple('Parameter','name type value desc dumps loads')

def Number(name, type=float, value=0.0, desc='Number'):
    return Parameter(name, type, value, desc, dumps=str, loads=type)
def String(name, type=str, value='', desc='String'):
    return Parameter(name, type, value, desc, dumps=lambda x:x, loads=lambda x:x)
def FileName(name, type='input', value='', desc='A file name'):
    return String(name, type, value, desc)
             

class ParameterSet(OrderedDict):
    
    def replace(self, name, **kwds):
        '''
        Replace entries given by keyword arguments in the parameter of the given name.
        '''
        self[name] = self[name]._replace(**kwds)

    def dumps(self):
        '''
        Return a pickle dump string representation of self.
        '''
        ret = OrderedDict()
        for n, p in self.items():
            ret[n] = p.loads(p.value)
        return pickle.dumps(ret)

    def loads(self, string):
        '''
        Load a dump string back into self.
        '''
        od = pickle.loads(string)
        for n, v in od.items():
            p = self[n]
            self.replace(n, value=p.loads(v))
        return

    def get_values(self):
        '''
        Return an ordered dict of the values
        '''
        return OrderedDict([(n,p.value) for n,p in self.items()])

    def set_values(self, **values):
        '''
        Set values from keyword arguments.  Only matching keys are used.
        '''
        for name, p in self.items():
            try:
                v = values[name]
            except KeyError:
                continue
            self.replace(name, value=v)
        return
