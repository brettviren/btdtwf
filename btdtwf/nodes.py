#!/usr/bin/env python
'''
Some particular node patterns
'''


class ConnectError(Exception):
    def __init__(self, msg, node, **kwds):
        self.msg,self.node.self.kwds = msg,node,kwds
    def __str__(self):
        return '%s (node="%s")' % (self.msg, self.node)

class ProgramNode(object):
    def __init__(self, cmdline, logfile = None, **kwds):
        self._cmdline = cmdline
        self._logfile = logfile
        self._kwds = {k:lambda:v for k,v in kwds.items()}
    def connect(self, node, name=None, **kwds):
        if name is None:
            raise ConnectError('No name given', node, **kwds)
        self._kwds[name] = node
    def __call__(self):
        from subprocess import Popen, PIPE, STDOUT

        kwds = {k:v() for k,v in self._kwds.items()}
        cmdstr = self._cmdline.format(**kwds)
        print 'Running:',cmdstr

        proc = Popen(cmdstr, shell=True, stdout=PIPE, stderr=STDOUT)
        code = proc.wait()
        if self._logfile:
            with open(self._logfile,'a') as fp:
                fp.write(proc.stdout.read())

        return code
        
class FileIONode(object):
    '''
    Interpret file names.
    '''
    pass
