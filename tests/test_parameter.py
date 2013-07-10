#!/usr/bin/env python

import btdtwf.parameter as bp

def test_make_some():
    s1 = bp.String('string1')
    f1 = bp.FileName('filename1')
    assert s1 and f1

def test_ps():
    old_filename = 'old_filename.txt'
    new_filename = 'new_filename.txt'

    ps1 = bp.ParameterSet(s=bp.String('string1'), f=bp.FileName('filename1',value=old_filename))
    ps2 = bp.ParameterSet(**ps1)
    assert ps1 == ps2
    d1 = ps1.dumps()
    d2 = ps2.dumps()
    assert d1 == d2

    ps2.replace('s', value='string2')
    assert ps2['s'].value == 'string2'
    assert ps1 != ps2
    ps2.loads(d1)
    assert ps1 == ps2

    ps3 = bp.ParameterSet(**ps1)
    ps3.replace('f', value=new_filename)
    assert ps3['f'].value == new_filename
    assert ps3 != ps1
    ps3.replace('f', value=old_filename)    
    assert ps3['f'].value == ps1['f'].value, (ps3['f'].value,  ps1['f'].value)

    assert ps1['f'].value != new_filename
    ps3 = bp.ParameterSet(**ps1)
    v1 = ps1.get_values()
    v1['f'] = new_filename
    ps1.set_values(**v1)
    ps3.replace('f',value=new_filename)
    assert ps1 == ps3
    assert ps1['f'].value == new_filename

if '__main__' == __name__:
    test_make_some()
    test_ps()
