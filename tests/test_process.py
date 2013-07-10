def test():
    from bein import MiniLIMS
    
    datafilepat = 'datafile_{x}.txt'
    p1_in = [
        Parameter(name='x', type=int, default=10, desc='a number'),
        Parameter(name='datafile', type='output', default=datafilepat,
                  desc='Data file holding x = {x}'),
        ]
    p1_out = [
        Parameter(name='y', type=float, default=20, desc='f(x)'),
        ]

    p2_in = [
        Parameter(name='y', type=float, default=30, desc='y=f(x)'),
        Parameter(name='z', type=int, default=40, desc='a number'),
        Parameter(name='indatafile', type='input', default=datafilepat,
                  desc='Data file holding x = {x}'),
        Parameter(name='outdatafile', type='output', default='out2data.txt',
                  desc='Data file holding some stuff'),
        ]
    p2_out = [
        Parameter(name='result', type=str, default='(unknown)', 
                  desc='some string result'),
        ]

    def callable1(ex, **kwds):
        print 'callable1', kwds
        x = kwds['x']
        datafile = kwds['datafile']
        with open(datafile, 'w') as fp:
            fp.write('# %s\n' % ', '.join(['%s:%s'%kv for kv in kwds.items()]))
            fp.write('x = %d\n' % x)
        return dict(y=float(x*x), datafile=datafile)

    def callable2(ex, **kwds):
        print 'callable2',kwds
        contents = [', '.join(['%s:%s'%kv for kv in kwds.items()])]

        outdatafile = kwds['outdatafile']
        with open(kwds['indatafile']) as infp:
            with open(outdatafile, 'w') as outfp:
                text = infp.read()
                outfp.write(text)
                contents.append(text)
        return dict(result='\n'.join(contents), outdatafile=outdatafile)

    M = MiniLIMS('test_process')
    pt1 = ProcessTask(M, 'ProcessTask#1',callable1, p1_in, p1_out)
    pt2 = ProcessTask(M, 'ProcessTask#2',callable2, p2_in, p2_out)

    wf = pyutilib.workflow.Workflow()
    pt2.inputs.indatafile = pt1.outputs.datafile
    pt2.inputs.y = pt1.outputs.y

    wf.add(pt1)
    print wf(x=999, z=1001)

if '__main__' == __name__:
    test()

