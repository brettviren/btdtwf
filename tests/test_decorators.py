#!/usr/bin/env python

from btdtwf.decorators import named_edges, format_dict, save_result, cached_result

def dump_dict(d, tab='\t'):
    print '\n'.join(['%s%s:%s'%(tab,k,v) for k,v in d.items()])

def test_named_edges():
    
    @ named_edges
    def taking_kwds(kwds):
        print 'taking_kwds()'
        dump_dict(kwds)
        return len(kwds)

    od = dict(thing1 = dict(a=1,b=2,name='name1'),
              thing2 = dict(b=3,c=4,name='name2'))
    r = taking_kwds(od)
    print r
    

def test_format_dict():
    
    @ format_dict
    def wanting_format(kwds):
        print 'wanting_format()'
        dump_dict(kwds)
        for v in kwds.values():
            if isinstance(v, basestring):
                assert '{' not in v 
        return len(kwds)

    d = dict(a = 'a{b}b', b=42)
    r = wanting_format(d)
    print r


def test_ne_fd():

    @ named_edges
    @ format_dict
    def wanting_format(kwds):
        print 'Named and formatted:'
        dump_dict(kwds)
        for v in kwds.values():
            if isinstance(v, basestring):
                assert '{' not in v 
        return len(kwds)

    od = dict({object(): dict(a=1,b=2,name='name1',infile='input_{a}_{b}_{c}.txt'),
               object(): dict(b=3,c=4,name='name2',outfile='ouput_{a}_{b}_{c}.txt')})
    r = wanting_format(od)
    print r


def test_save_result():

    @ format_dict
    @ save_result('result_file')
    def do_something(inputs):
        return len(inputs)

    d = dict(result_file='outputs_{a}_{b}.txt', a=1, b='boing')
    r = do_something(d)
    print r


def test_cached_result():
    
    @ format_dict
    @ cached_result('result_file')
    def do_something(inputs):
        return len(inputs)

    cache_file_name = 'cached_outputs_{a}_{b}.txt'
    d = dict(result_file=cache_file_name, a=1, b='boing')

    r = do_something(d)
    print r

    r = do_something(d)
    print r

if '__main__' == __name__:
    # test_named_edges()
    # test_format_dict()
    # test_ne_fd()
    # test_save_result()
    test_cached_result()
