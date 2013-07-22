#!/usr/bin/env python

import os
from contextlib import contextmanager

@contextmanager
def cd(path):
    old = os.getcwd()
    os.chdir(path)
    yield old
    os.chdir(old)

def format_flat_dict(dat, formatter = str.format, **kwds):
    '''Return a formatted version of <dat> its own items with string
    values and any extra given by <kwds> by calling <formatter>.

    '''

    kwds = dict(kwds)
    unformatted = dict(dat)
    formatted = dict()

    while unformatted:
        changed = False
        for k,v in unformatted.items():
            if not isinstance(v, basestring):
                formatted[k] = v
                kwds[k] = v
                unformatted.pop(k)
                changed = True
                continue
            try:
                new_v = formatter(v, **kwds)
            except KeyError:
                continue        # maybe next time
            changed = True
            formatted[k] = new_v
            kwds[k] = new_v
            unformatted.pop(k)
            continue
        if not changed:
            break
        continue
    if unformatted:
        formatted.update(unformatted)
    return formatted
