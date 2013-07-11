#!/usr/bin/env python


import btdtwf.result as br
import btdtwf.parameter as bp
from bein import MiniLIMS, execution

procname = 'procname'
ips = bp.ParameterSet(a=bp.Number(1), b=bp.Number(2))
ops = bp.ParameterSet(x=bp.Number(42.0), y=bp.Number(6.9), 
                      out=bp.FileName('test_result_out', 'output file for test_result', 'output'))


def test_result_name():
    want = 'foo.a3735805180ed0739fa420274b996047ae0d8d8c.result'
    got = br.result_name('foo',dict(a=1,b=2,c=3))
    assert want == got

def test_loop():
    M = MiniLIMS('test_result')

    with execution(M) as ex:
        br.prepare(ex, procname, ips)
        with open('test_result_out','w') as fp:
            fp.write('test_result\n')
        br.finish(ex, procname, ips, ops)

def test_cache():
    M = MiniLIMS('test_result')
    ts = br.timestamp(M, procname, ips.get_values())
    assert ts

    r = br.result(M, procname, ips.get_values())
    assert r == ops.get_values()

    res = br.cached(M, procname, ips)
    assert res == ops.get_values()

    missing = br.cache(M, 'wrongname', ips)
    assert missing is None

if '__main__' == __name__:
    test_result_name()
    test_loop()
    test_cache()

