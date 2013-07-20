#!/usr/bin/env python

from collections import OrderedDict

def test_arg_mutate():
    
    def nodes_to_kwds(f_taking_kwds):
        def wrap(node_data):
            print node_data
            kwds = OrderedDict()
            for node,data in node_data.items():
                name = data.pop('name')
                print name
                kwds[name] = node
                for k,v in data.items():
                    kwds[k]=v 
            return f_taking_kwds(kwds)
        return wrap

    @nodes_to_kwds
    def taking_kwds(kwds):
        print kwds
        return len(kwds)

    od = OrderedDict()
    od['thing1'] = dict(a=1,b=2,name='name1')
    od['thing2'] = dict(b=3,c=4,name='name2')
    r = taking_kwds(od)
    print r


def test_dec_func():

    def onetwo(n):
        print 'onetwo(%s)' % n
        def wrap(f):
            def wrapped_f():
                print 'wrapped(%s)' % f
                return f(1,n)
            return wrapped_f
        return wrap

    @ onetwo(2)
    def myfunc(a, b):
        print 'myfunc(%s,%s)'%(a,b)
        return a+b

    print 'myfunc is:',myfunc,'calling now:'
    r = myfunc()
    print 'returns',r

if '__main__' == __name__:
    #test_dec_func()
    test_arg_mutate()
