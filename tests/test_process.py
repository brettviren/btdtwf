#!/usr/bin/env python
'''
Test processing
'''

from btdtwf import workflow, bein, process, parameter

def test():

    datafilepat = 'datafile_{x}.txt'
    p1_in = parameter.ParameterSet(
        x = parameter.Number(10, desc='a number'),
        datafile = parameter.FileName(datafilepat, hint='output', desc='Data file holding x = {x}'),
        )
    p1_out = parameter.ParameterSet(
        y = parameter.Number(20, desc='f(x)'),
        )

    p2_in = parameter.ParameterSet(
        y = parameter.Number(30, desc='y=f(x)'),
        z = parameter.Number(40, desc='a number'),
        indatafile = parameter.FileName(datafilepat, hint='input',
                                 desc='Data file holding x = {x}'),
        outdatafile = parameter.FileName('out2data.txt', hint='output', 
                                  desc='Data file holding some stuff'),
        )
    p2_out = parameter.ParameterSet(
        result = parameter.String('', desc='some string result'),
        )

    def callable1(ex, **kwds):
        print 'callable1', kwds
        x = kwds['x']
        datafile = kwds['datafile']
        with open(datafile, 'w') as fp:
            fp.write('# %s\n' % ', '.join(['%s:%s'%kv for kv in kwds.items()]))
            fp.write('x = %d\n' % x)
        return dict(y=float(x*x), out_datafile=datafile)

    def callable2(ex, **kwds):
        print 'callable2',kwds
        contents = [', '.join(['%s:%s'%kv for kv in kwds.items()])]

        outdatafile = kwds['outdatafile']
        with open(kwds['indatafile']) as infp:
            with open(outdatafile, 'w') as outfp:
                text = infp.read()
                outfp.write(text)
                contents.append(text)
        result = '|'.join(contents)
        return dict(result='"%s"'%result, out_outdatafile=outdatafile)


    wf = workflow.Workflow()

    pt1 = process.register('TaskN1',callable1, p1_in, p1_out)
    print 'pt1.id=',pt1.id
    pt2 = process.register('TaskN2',callable2, p2_in, p2_out)
    print 'pt2.id=',pt2.id

    pt2.inputs.indatafile = pt1.outputs.out_datafile
    pt2.inputs.y = pt1.outputs.y

    print 'wf.id=',wf.id
    #wf.debug = True
    wf.add(pt1)

    res = wf(provenance_name='test_process', x=999, z=1001)

    print 'wf(x=999, z=1001):'
    print '              y =',res.y
    print '         result =',res.result
    print '   out_datafile =',res.out_datafile
    print 'out_outdatafile =',res.out_outdatafile
    print 'everything=',res
if '__main__' == __name__:
    test()

