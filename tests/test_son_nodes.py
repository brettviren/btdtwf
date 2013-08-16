#!/usr/bin/env python 

from btdtwf.son.nodes import CallableNode, ProgramCallable, callable_program

def chirp(cons, **kwds):
    print '%d cons, %d kwds' % (len(cons), len(kwds))
    print 'cons:'
    for icon,(node,ckwds) in enumerate(cons.items()):
        val = node()
        print '\t%d: %s %s' % (icon,str(val),str(ckwds))
    print 'kwds:', kwds
    return sum((len(cons), len(kwds)))

def test_son_callable():
    cn = CallableNode(chirp, a=1,b=2)
    cn.connect(lambda:4, a=10, c=4)
    cn.connect(lambda:5, a=20, d=5)
    val1 = cn()
    val2 = cn()
    print val1
    assert val1 == val2

def test_son_program():
    import StringIO
    myout = StringIO.StringIO()
    cmdline = '{program} {name1} {name2} {arg_a} {arg_b} {arg1} {arg2} {abcd}'
    #pc = ProgramCallable(cmdline, logfile=myout, a="frompc", b=1, program='/bin/echo')
    pc = callable_program(cmdline, logfile=myout, a="frompc", b=1, program='/bin/echo')
    cn = CallableNode(pc, b=2, name1='hello')
    cn.connect(lambda:4, a=10, c=4, name='arg_a', name2='world')
    cn.connect(lambda:5, a=20, d=5, name='arg_b', abcd="{a}-{b}-{c}-{d}")
    val1 = cn()
    val2 = cn()
    assert val1 == val2
    print 'Called:',pc.called
    print 'Output:',myout.getvalue().strip()
    print 'Returned:',val1
    

if '__main__' == __name__:
    #test_son_callable()
    test_son_program()

