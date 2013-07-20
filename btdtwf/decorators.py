#!/usr/bin/env python

import os
import json
from collections import OrderedDict
from util import format_flat_dict

def named_edges(f_taking_kwds):
    'dict(nodeX=dict(name="foo", a=1), ...) --> dict(foo=nodeX, a=1)'
    def wrap(node_data):
        kwds = OrderedDict()
        for node,data in node_data.items():
            name = data.pop('name')
            kwds[name] = node
            for k,v in data.items():
                kwds[k]=v 
        return f_taking_kwds(kwds)
    return wrap

def format_dict(f_wanting_format):
    def wrap(data):
        fdata = format_flat_dict(data)
        data.update(fdata)
        return f_wanting_format(data)
    return wrap

def save_result(result_filename_key, dumps = lambda d: json.dumps(d, indent=2)):
    def wrapper(f_to_save):
        def wrap(inputs):
            fname = inputs[result_filename_key]
            result = f_to_save(inputs)
            with open(fname,'w') as fp:
                to_save = (inputs, result)
                fp.write(dumps(to_save))
            return result
        return wrap
    return wrapper

def cached_result(result_filename_key,
                  dumps = lambda d: json.dumps(d, indent=2),
                  loads = json.loads):
    def wrapper(f_to_maybe_run):
        def wrap(inputs):
            fname = inputs[result_filename_key]
            if os.path.exists(fname):
                with open(fname) as fp:
                    cached_inputs, cached_results = loads(fp.read())
                if dumps(cached_inputs) == dumps(inputs):
                    print 'Cache hit (%s)' % fname
                    return cached_results
            
            results = f_to_maybe_run(inputs)
            with open(fname, 'w') as fp:
                fp.write(dumps((inputs,results)))
            print 'Cached (%s)' % fname
            return results
        return wrap
    return wrapper


                        

                    
