#!/usr/bin/env python
'''
A Process encapsulates a task or a procedure which takes some input
and produces some output.  The feeding of input to and accepting of
output from the process is managed in order to provide 

 - pipelines to be produced by connecting one process output to
   another process input

 - where possible, input and output data are saved to file and
   recorded in a provenance catalog

 - the task is only run if the expected output does not yet exist or
   is older than any of the input.

A Process consists of three parts:

 - a description of expected input parameters

 - a description of expected output values

 - a callable taking input parameters and producing output values

The collections of input or output parameter descriptions are in the
form of a sequence Parameter instances.  The input and output values
are of the form of keyword arguments to the callable or a dictionary,
respectively.

The callable is called like:

  callable(ex, **kwds)  -->  dict

The each keyword argument corresponds to one element of the input
parameter description collection.  Each item in the returned dict must
correspond to an element in the output parameter description
collection.  In both cases the keys are taken from the name attribute
of the Parameter.

Input and output files are handled specially.  In both cases their
names are specified as input parameters.  They are indicated with a
special type represented by the string "input" or "output".

Both input and output filenames may include "{...}" formatting
variables which will be resolved using the input values.

Formatted "input" file names are interpreted as file catalog aliases and
if found will be replaced by a file catalog path and the file stats
noted.

Formatted "output" file names are likewise checked in the catalog.  If
they already exist and with a time stamp newer than all input files
the callable will not be called.

'''

from collections import namedtuple, OrderedDict
import pyutilib.workflow
from bein import execution
import pickle

Parameter = namedtuple('Parameter','name type default desc dumps loads')

def Number(name, type=float, default=0.0, desc='A number'):
    return Parameter(name,type,default,desc,dumps=str,loads=type)
def String(name, type=str, default='', desc='A string'):
    return Parameter(name,type,default,desc,dumps=lambda x:x, loads=lambda x:x)
def FileName(name, type='input', default='', desc='A file name'):
    return String(name, type, default, desc)
             

tasks = dict()

class ProcessTask(pyutilib.workflow.Task):
    def __init__(self, minilims, name, callable, input_params, output_params,
                 *args, **kwds):
        super(ProcessTask, self).__init__(*args, name=name, **kwds)
        self.M = minilims
        self.callable = callable

        self.op = OrderedDict()
        self.ip = OrderedDict()

        for p in output_params:
            self.op[p.name] = p
            self.outputs.declare(p.name, default=p.default, doc=p.desc)
        for p in input_params:
            self.ip[p.name] = p
            self.inputs.declare(p.name, default=p.default, doc=p.desc)
            if p.type == 'output' and not p.name in self.op.keys():
                self.op[p.name] = p
                self.outputs.declare(p.name, default=p.default, doc=p.desc)

        global tasks
        tasks[name] = self
        return

    def get_values(self, params = None):
        'Return ordered dictionary of values corresponding to input params'
        params = params or self.ip
        ret = OrderedDict()
        for n,p in params.items():
            v = getattr(self, n)
            ret[n] = v
        return ret
        
    def dumps_values(self, params = None):
        '''
        Return values from self into string representation of values
        corresponding to input params.'''
        params = params or self.ip
        od = OrderedDict()
        for n,p in params.items():
            v = getattr(self, n)
            od[n] = p.dumps(v)
        return pickle.dumps(od)

    def loads_values(self, string, params = None):
        '''Load values into self corresponding to output params.'''
        params = params or self.op
        od = pickle.loads(string)
        ret = OrderedDict()
        for n,v in od.items():
            p = params[n]
            v = p.loads(v)
            ret[n] = v
            setattr(self, n, v)
        return ret

    def get_sha1(self, params = None):
        'Return a sha1 of our input'
        import hashlib
        sha = hashlib.sha1()
        sha.update(self.dumps_values(params))
        return sha




    def get_input(self):

        invar = dict()
        input_files = dict()
        output_files = dict()

        for p in self.ip:
            val = getattr(self, p.name) # set through pyutilib.workflow

            if p.type == "input":
                input_files[p.name] = val
                continue
            if p.type == "output":
                output_files[p.name] = val
                continue

            invar[p.name] = val

        newest_input = None
        for key,val in input_files.items():
            try:
                fname = val.format(**invar)
            except KeyError:
                print 'Failed to format input file: "%s"' % val
                raise

            try:
                fstat = self.M.fetch_file(fname)
            except ValueError:  # outside bein control
                invar[key] = fname
                continue

            ts = fstat['created']
            if newest_input is None or newest_input < ts:
                newest_input = ts
            invar[key] = self.M.path_to_file(fname)

        do_run = False
        for key,val in output_files.items():
            try:
                fname = val.format(**invar)
            except KeyError:
                print 'Failed to format output file "%s"' % val
                raise

            try:
                fstat = self.M.fetch_file(fname)
            except ValueError:  # doesn't yet exist
                invar[key] = fname
                do_run = True
                continue

            invar[p.name] = self.M.path_to_file(fname)

            ts = fstat['created']
            if newest_input and ts < newest_input:
                do_run = True
                continue
            continue

        return (do_run, invar, output_files)

    def set_output(self, outfiles, **kwds):
        print 'Output of "%s"' % self.name

        for key, val in kwds.items():
            setattr(self, key, val)

        for key, val in outfiles.items():
            if key in kwds.keys():
                continue
            setattr(self, key, val)

        # fixme: need to handle saving of files into catalog...
        #self.M.add(outdatafile, alias=outdatafile)


        print self.name,'INPUTS'
        for p in self.ip:
            print '\t',p.name,getattr(self,p.name)
        print self.name,'OUTPUTS'
        for p in self.op:
            print '\t',p.name,getattr(self,p.name)

    def run(self, **kwds):
        with execution(self.M, description=self.name) as ex:
            outvar = self.callable(ex, **kwds)
        return outvar

    def execute(self):

        do_run, invar, outfiles = self.get_input()

        do_run = True

        if do_run:
            outvar = self.run(**invar)
        else:
            print 'No need to run:\n%s\n' % (invar)
            outvar = self.get_cached(**invar)
        
        # fixme: vet the outvars, maybe handle any pure-output files?
        self.set_output(outfiles, **outvar)
            
        return

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

