#!/usr/bin/env python

import os
from subprocess import Popen, PIPE
from contextlib import contextmanager

@contextmanager
def cd(path):
    old = os.getcwd()
    os.chdir(path)
    yield old
    os.chdir(old)

class GitError(Exception):
    def __init__(self, cmdstr, out, err):
        self.cmdstr,self.out,self.err = cmdstr,out,err
        super(GitError, self).__init__()
    def __str__(self):
        if not self.err:
            return 'Git error: "%s" output:\n%s\n' % (self.cmdstr, self.out)
        return 'Git error: "%s" output:\n%s\nerror:\n%s' % (self.cmdstr, self.out, self.err)


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
        with cd(indir):
            #print 'Running: %s in %s' % (str(cmdlist), os.getcwd())
            proc = Popen(cmdstr, shell=True, stdout=PIPE, stderr=PIPE)
            if proc.wait() != 0:
                raise GitError(cmdstr, proc.stdout.read(), proc.stderr.read())
            return (proc.stdout.read(), proc.stderr.read())
            
    def initialized(self):
        return os.path.exists(self.gitdir)

    def dirty(self):
        self('status -s')

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
            with self.execute(None, 'Staring Point', 'start'):
                with open('.gitignore','w') as fp:
                    fp.write('*~\n')

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
        with cd(self.git.workdir):
            if start:
                self.git('checkout %s' % start)
            try:
                yield self
                self.git('commit -a -m "%s"' % description)
                if tag:
                    self.git('tag -f %s' % tag)
            except GitError:    # rewind
                if start:
                    self.git('reset --hard %s' % start)
                raise

#------------------
        
def test_cd():
    print os.getcwd()
    with cd('/tmp') as oldir:
        print oldir
        print os.getcwd()
    print os.getcwd()

def test_make_git():
    git = Git('/tmp/got')
    try:
        print git('status')
    except GitError:
        print 'Got expected git error'
    else:
        raise ValueError,'Did not get expected git error, did /tmp/got already exist?'


def test_got(num):
    g = Got('/tmp/got')
    print 'TAGS:',g.tags()
    with g.execute('start', 'First pass', 'testtag%d'%num):
        with open('somefile.txt','w') as fp:
            fp.write('got testing?\n')

    with g.execute('testtag%d'%num, 'Mutate, Exterminate, Eliminate', 'follow-on%d'%num):
        with open('somefile.txt') as inp:
            with open('copyfile.txt','w') as out:
                out.write(inp.read())
        

if __name__ == '__main__':
    test_cd()
    test_make_git()
    test_got(1)
    test_got(2)
