#!/usr/bin/env python

from btdtwf.util import format_flat_dict

def test_format_flat_dict():
    d = dict(a='a{b}a', b=2)
    d2 = format_flat_dict(d)
    print d2

if '__main__' == __name__:
    print test_format_flat_dict()
