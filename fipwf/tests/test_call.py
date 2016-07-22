#!/usr/bin/env python3
'''
This sketches the idea for calling one node in a fipwf.

'''

import json
import hashlib

def signature(obj):
    s = hashlib.sha1()
    s.update(json.dumps(obj).encode('utf-8'))
    return s.hexdigest()

def function_name(fun):
    if hasattr(fun,'name'): return fun.name
    if hasattr(fun,'__name__'): return fun.__name__
    return str(fun)
def function_version(fun):
    if hasattr(fun,'version'): return fun.version
    if hasattr(fun,'__version__'): return fun.__version__
    return str(fun)             # punt...

def Fsig(fun):
    return signature((function_name(fun), function_version(fun)))
def PSsig(**params):
    return signature(params)
def RSspec(*result_sigs):
    return tuple(*result_sigs)
def Tspec(fsig, rsspec, psig):
    return tuple(fsig, rsspec, psig)
def Rsig(tspec):
    return signature(tspec)



## Some function primatives

def makenum(number=None, *rs, **ps):
    return number
makenum.version = '1.0'

def adder(*rs, **ps):
    print ('adding: %s' % (str(rs)))
    adder.calls += 1
    return sum(rs)
adder.version = '1.0'
adder.calls = 0

def avger(*rs, **ps):
    print ('averaging: %s' % (str(rs)))
    avger.calls += 1
    return sum(rs) / len(rs)
avger.version = '1.0'
avger.calls = 0

class Context(object):
    '''
    A dumb FIPWF context.
    '''

    def __init__(self):
        self.functions = dict() # Fsig -> function
        self.paramsets = dict() # PSsig -> paramset
        self.tasks = dict() # Rsig -> tspec
        self.results = dict() # Rsig -> result object

    def function(self, func):
        fsig = Fsig(func)
        self.functions[fsig] = func
        return fsig
    
    def paramset(self, **params):
        psig = PSsig(**params)
        self.paramsets[psig] = params
        return psig

    def task(self, fsig, rsspec, psig):
        tspec = (fsig, rsspec, psig)
        rsig = Rsig(tspec)
        self.tasks[rsig] = tspec
        return rsig

    def resolve_function(self, fsig):
        return self.functions[fsig]

    def resolve_paramset(self, psig):
        return self.paramsets[psig]

    def resolve_result(self, rsig):
        try:
            return self.results[rsig]
        except KeyError:
            pass
        tspec = self.tasks[rsig]
        fsig, rsspec, psig = tspec

        func = self.resolve_function(fsig)
        rs = tuple(self.resolve_result(r) for r in rsspec)
        ps = self.resolve_paramset(psig)

        result = func(*rs, **ps)
        self.results[rsig] = result
        return result

        
def test_context():
    c = Context()
    p0 = c.paramset()
    p1 = c.paramset(number=1)
    p2 = c.paramset(number=2)
    fmak = c.function(makenum)
    favg = c.function(avger)
    fadd = c.function(adder)

    t1 = c.task(fmak, (), p1)
    t2 = c.task(fmak, (), p2)

    tadd = c.task(fadd, (t1, t2), p0)
    tavg = c.task(favg, (t1, t2), p0)
    tadd2 = c.task(fadd, (tadd, tavg), p0)

    for k,v in locals().items():
        print ("%s %s"%(v,k))

    radd = c.resolve_result(tadd)
    print ('radd: %s' % radd)

    radd2 = c.resolve_result(tadd2)
    print ('radd2: %s' % radd2)

    print ('adder.calls = %d' % adder.calls)
    assert adder.calls == 2
    print ('avger.calls = %d' % avger.calls)    
    assert avger.calls == 1

def test_sugar():
    c = Context()

    def myadd(a,b):
        return c.resolve_result(c.task(c.function(adder),
                                       (c.task(c.function(makenum), (),
                                               c.paramset(number=a)),
                                        c.task(c.function(makenum), (),
                                               c.paramset(number=b))),
                                       c.paramset()))

    answer = myadd(1,2)
    print ("1 + 2 = %s" % answer)
        

if '__main__' == __name__:

    test_context()
    test_sugar()



