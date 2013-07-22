#!/usr/bin/env python

import os
from subprocess import Popen, PIPE
from contextlib import contextmanager
import util


class GitError(Exception):
    def __init__(self, cwd, cmdstr, out, err):
        self.cwd,self.cmdstr,self.out,self.err = cwd,cmdstr,out,err
        super(GitError, self).__init__()
    def __str__(self):
        msg = ['error from command: <%s>' % self.cmdstr]
        if self.out:
            msg.append('Output: \n%s' % self.out)
        if self.err:
            msg.append('Error: \n%s' % self.err)
        msg.append('In: %s' % self.cwd)
        msg.append('Return the repository to a clean state manually.')
        return '\n'.join(msg)



class Git(object):
    exe = 'git'

    def __init__(self, workdir):
        '''
        Create a git executable associated to the working directory.  

        The working directory will be created git-init'ed if needed.
        '''
        if not os.path.exists(workdir):
            os.makedirs(workdir)
        self.workdir = workdir
        self.gitdir = os.path.join(workdir,'.git')

    def __call__(self, cmd, indir = None):
        indir = indir or self.workdir
        if isinstance(cmd, basestring):
            cmd = cmd.split()
        cmdlist = [self.exe] + cmd
        cmdstr = ' '.join(cmdlist)
        with util.cd(indir):
            #print 'Running: %s in %s' % (str(cmdlist), os.getcwd())
            proc = Popen(cmdstr, shell=True, stdout=PIPE, stderr=PIPE)
            if proc.wait() != 0:
                ge = GitError(self.workdir, cmdstr, proc.stdout.read(), proc.stderr.read())
                raise ge 
            return (proc.stdout.read(), proc.stderr.read())
            
    def initialized(self):
        return os.path.exists(self.gitdir)

    def dirty(self):
        return self('status -s') != ('','')

    def status(self):
        return [x.split() for x in self('status -s')[0].split('\n') if x]


class Got(object):
    '''
    Git Object Tracker

    Got provides a context manager for executing code which produces
    files and uses git as a backend to track the files in the
    associated working directory.  
    '''

    def __init__(self, workdir):
        '''
        Connect to the workdir.
        '''
        if not os.path.exists(workdir):
            os.makedirs(workdir)
        self.git = Git(workdir)            
        if not self.git.initialized():
            self.git('init')
            with self.execute(None, 'Staring Point', 'start') as g:
                with open('.gitignore','w') as fp:
                    fp.write('*~\n')
                g.add('.gitignore')

    def add(self, filename):
        'Add the given file to the tracker.'
        self.git('add %s' % filename)

    def remove(self, filename):
        'Remove the given file to the tracker.'
        self.git('remove %s' % filename)

    def tags(self):
        return [x for x in self.git('tag')[0].split('\n') if x]


    @contextmanager
    def execute(self, start, description, tag = None):
        with util.cd(self.git.workdir):
            if start:
                self.git('checkout %s' % start)

            yield self

            if self.git.dirty():
                self.git('commit -a -m "%s"' % description)
                if tag:
                    self.git('tag -f %s' % tag)
            else:
                print 'Got: no change detected.'





