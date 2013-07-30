#!/usr/bin/env python
'''
Some particular nodes and node patterns that work together
'''

import os
from collections import OrderedDict
from exception import CallError
from btdtwf.util import format_flat_dict
from subprocess import Popen, PIPE, STDOUT
import json

class BaseNode(object):
    '''
    Basic node to collect connections and provide in-memory cache.

    Sub-classes should implement ``run()``
    '''
    def __init__(self, **node_kwds):
        self._node_kwds = node_kwds
        self._connections = OrderedDict()

    def connect(self, node, **kwds):
        '''Add an edge connection to a node.

        Args:
            node (callable): the node to call

            kwds (dict): keyword arguments to associate with the edge
        '''

        self._connections[node] = kwds

    def run(self):
        raise CallError('unimplemented', self)

    def __call__(self):
        if hasattr(self, '_cache'):
            return self._cache
        self._cache = self.run()
        return self._cache


class CallableNode(BaseNode):
    '''An adapter node to call a callable.'''

    def __init__(self, callable, **node_kwds):
        '''A node given a callable
        Args:
            callable (callable): the callable to call
        
            node_kwds (dict): keyword arguments passed along to call of callable
        
        The callable will be called as::

            callable(connections, **node_kwds)

        The ``connections`` is a ``OrderedDict`` keyed by an input
        node and with values consisting of any edge connection keyword
        arguments.
        '''
        self._callable = callable
        super(CallableNode,self).__init__(**node_kwds)

    def run(self):
        '''Call the callable'''
        return self._callable(self._connections, **self._node_kwds)

def connection_keywords(connections, **kwds):
    '''Return a unified dictionary of connection information.

    Args:
        connections (OrderedDict): mapping of node objects to their edge connection dictionaries.

        kwds (dict): any initial default

    Returns:

        dict.  The union of values.

    The resulting dict is formed from a cascade of sources, each
    potentially overriding the previous:

    - ``kwds`` keyword arguments passed to the function

    - edge connection dictionaries in ``connections`` values
    
    - values from calling nodes in the ``connections`` keys

    In this last case, the values are available in two ways:

    - by argument number as labeled "argN" (ie, arg1, arg2, etc) 

    - by name if the connections values have a 'name' keyword item

    '''
    p = dict(kwds)
    for iarg, (node,kwds) in enumerate(connections.items()):
        kwds = dict(kwds)   # copy
        value = node()
        argn = 'arg%d' % (iarg+1,)
        kwds[argn] = value
        arg_name = kwds.get('name')
        if arg_name:
            kwds[arg_name] = value
        p.update(kwds)
    return p


class ProgramCallable:
    '''Callable to exec a command line in a sub-shell.
    '''
    def __init__(self, cmdline, log="/dev/stdout", **kwds):
        '''Create a program callable
        
        Args:
            cmdline (string): a shell command line, with str.format() codes

            log (None, str or file object): string implies a filename
            to which any stdout is appended, None implies output is
            discarded.  Anything else will be assumed to be a
            file-like object.

            kwds (dict): default keyword arguments for str.format()

        The ``cmdline`` string may contain ``str.format()`` codes
        which will be resolved from keyword arguments passed here,
        added at connection time or taken from the value of the
        connected nodes.  See ``connection_keywords`` for more
        information.

        Example:

        >>> cmdline = '{program} {name1} {name2} {arg_a} {arg_b} {arg1} {arg2}'
        >>> pc = ProgramCallable(cmdline, a="frompc", b=1, program='/bin/echo')
        >>> cn = CallableNode(pc, b=2, name1='hello')
        >>> cn.connect(lambda:4, a=10, c=4, name='arg_a', name2='world')
        >>> cn.connect(lambda:5, a=20, d=5, name='arg_b')
        >>> print pc.returned
        None
        >>> print cn()
        0
        >>> print pc.called
        /bin/echo hello world 4 5 4 5
        >>> print pc.returned
        0

        '''
        self._cmdline = cmdline
        if isinstance(log, basestring):
            log = open(log,'a')
        self._log = log
        self._kwds = kwds
        self.called = None
        self.returned = None

    def execute(self, params):
        self.called = self._cmdline.format(**params)
        proc = Popen(self.called, shell=True, stdout=PIPE, stderr=STDOUT)
        ret = proc.wait()
        if not self._log:
            return self.returned
        self._log.write(proc.stdout.read())
        return ret

    def munge_inputs(self, connections, **kwds):
        inputs = dict(self._kwds, **connection_keywords(connections,**kwds))
        inputs = format_flat_dict(inputs)
        return inputs

    def run(self, connections, **kwds):
        inputs = self.munge_inputs(connections, **kwds)
        return self.execute(inputs)

def wrap_connection_keywords(**extra):
    '''Decorate a callable converting the node kwds plus the extra ones
    into connection keywords.  See ``connection_keywords()`` function
    for details.

    '''
    def wrapper(f):
        def wrap(connections, **kwds):
            extra.update(kwds)
            kwds = connection_keywords(connections, **extra)
            return f(connections, **kwds)
        return wrap
    return wrapper

def wrap_format_keywords(**extra):
    '''Decorate a callable to apply ``format_flat_dict()`` to the node
    kwds plus the extra ones.
    '''
    def wrapper(f):
        def wrap(connections, **kwds):
            kwds = format_flat_dict(kwds,**extra)
            return f(connections, **kwds)
        return wrap
    return wrapper

def connection_input_files(connections, **kwds):
    ret = []
    for node,edge in connections.items():
        filetype = edge.get('filetype')
        if not filetype:
            continue
        if filetype != 'input':
            continue
        fname = node().format(**kwds)
        ret.append(fname)
    return ret

def wrap_cache(store):
    '''Decorate a callable to apply a simple cache feature.'''
    def wrapper(f):
        def wrap(connections, **kwds):
            res = store.get(**kwds)
            if res:
                return res

            res = f(connections, **kwds)
            store.add(res, **kwds)
            return res
        return wrap
    return wrapper

class DummyStore:
    def add(self, res, **kwds):
        print 'Dummy store adding result "%s" from %s' % (res, kwds)
    def get(self, *files, **kwds):
        print 'Dummy store missing result for %s' % str(kwds)

def callable_program(cmdline, log='/dev/stdout', store=DummyStore(), **kwds):
    @ wrap_connection_keywords(**kwds)
    @ wrap_format_keywords()
    #@ wrap_cache(store)
    def the_callable(connections, **params):
        cmdstr = cmdline.format(**params)
        the_callable.called = cmdstr # for the curious
        proc = Popen(cmdstr, shell=True, stdout=PIPE, stderr=STDOUT)
        ret = proc.wait()
        if not log:
            return ret
        mylog = log
        if isinstance(log, basestring):
            mylog = open(log,'a')
        mylog.write(proc.stdout.read())
        return ret

    return the_callable



def wash_files(*fnames):
    ret = []
    for fname in fnames:
        if not fname:
            continue
        if fname[0] != '/':
            ret.append(fname)
            continue
        link = os.path.basename(fname) + '.url'
        with open(link,'w') as fp:
            fp.write(fname + '\n')
        ret.append(link)
    return ret
            

class GotNode(BaseNode):
    '''A node that calls its inputs in the context of a Got execution
    and interprets their results as names of files to be added to the
    Got store.  The returned values may either be a single filename of
    a sequence.'''
    def __init__(self, got, start, description, tag=None, **node_kwds):
        '''Create a GotNode

        Args:
            got (Got object): an instance of a Got

            start (string): a git tree-ish that should be used as the initial Got state

            description (string): a string to use to commit the result

            tag (string): an optional tag to place on the resulting commit

        Returns: list of files added.

        Note: this node will change to the Got directory before
        calling the input nodes.  It has not control over if the nodes
        have already been called or not.
        '''
        super(GotNode,self).__init__(**node_kwds)
        self._got = got
        self._start = start
        self._desc = description
        self._tag = tag


    def run(self):
        ret = []
        with self._got.execute(self._start, self._desc, self._tag) as got:
            for node,kwds in self._connections.items():
                r = node()
                if isinstance(r, basestring):
                    r = [r]

                r = wash_files(*r)
                got.add(' '.join(r))
                ret += r

        return ret
                
def got_callable(got, start, desc, tag=None):
    '''Wrap a callable so that its outputs are added to got.

    The wrapped callable should return a filename or a sequence of
    filenames that it produces.

    '''

    def wrapper(f_for_got):
        def wrap(connections, **kwds):

            # make sure nodes all fire outside influence of got in
            # case they too use got or otherwise would not like their
            # cwd changed.
            for node in connections:
                node()

            with got.execute(start, desc, tag) as g:
                r = f_for_got(connections, **kwds)
                if isinstance(r, basestring):
                    r = [r]
                r = wash_files(*r)
                g.add(' '.join(r))
                return r

        return wrap
    return wrapper

            
