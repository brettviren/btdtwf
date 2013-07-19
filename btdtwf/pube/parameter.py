#!/usr/bin/env python
'''
A parameter is a value with a description and a serialization hint.

A parameter set is an ordered dictionary of parameters keyed by their names.
'''

from collections import namedtuple, OrderedDict
import pickle

allowed_hints = ['input', 'output', 'pod', 'pickle', None]

Parameter = namedtuple('Parameter','value desc hint')


def Number(value=0, desc = "Number"):
    return Parameter(value, desc, 'pod')

def String(value='', desc='String'):
    return Parameter(value, desc, 'pod')

def FileName(value='', desc='FileName', hint='input'):
    return Parameter(value, desc, hint)
             

class ParameterSet(OrderedDict):
    
    def replace(self, name, **kwds):
        '''
        Replace entries given by keyword arguments in the parameter of the given name.
        '''
        self[name] = self[name]._replace(**kwds)

    def dumps(self):
        '''
        Return a (pickle) string representation of value set. (best effort)
        '''
        return pickle.dumps(self.get_values())

    def loads(self, string):
        '''
        Load a (pickle) dump string back into self. (best effort)
        '''
        od = pickle.loads(string)
        self.set_values(**od)

    def serializable(self):
        '''
        Return True if all parameters are serializable.
        '''
        for p in self.values():
            if p.hint is None:
                return False
        return True

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
