#!/usr/bin/env python

import os
from subprocess import Popen, PIPE
from contextlib import contextmanager

class cd:
    def __init__(self, path):
        self._path = path
    def __enter__(self):
        self._old = os.getcwd()
        os.chdir(self._path)
        return self._old
    def __exit__(self, et, ev, tb):
        os.chdir(self._old)

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
        if not os.path.exists(workdir):
            os.makedirs(workdir)
        self.workdir = workdir
        self._gitdir = os.path.join(workdir,'.git')
        if not os.path.exists(self._gitdir):
            self('init')
            with open(os.path.join(workdir,'.gitignore'), 'w') as fp:
                fp.write('*~\n')
            self('add .gitignore')
            self('commit -a -m "start"')
            self('tag start')

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
            

class Got(object):
    def __init__(self, workdir, treeish=None):
        self.git = Git(workdir)
            
    @contextmanager
    def execute(self, start, description, tag = None):
        with cd(self.git.workdir):
            self.git('checkout %s' % start)
            yield self.git
            self.git('add *')
            self.git('commit -a -m "%s"' % description)
            if tag:
                self.git('tag %s' % tag)

        
def test_cd():
    print os.getcwd()
    with cd('/tmp') as oldir:
        print oldir
        print os.getcwd()
    print os.getcwd()

def test_git_init():
    git = Git('/tmp/got')
    out,err = git('status')
    print out

def test_got():
    g = Got('/tmp/got')
    with g.execute('start', 'Just another Perl hater', 'testtag') as ex:
        print 'test_got in', os.getcwd()
        with open('somefile.txt','w') as fp:
            fp.write('got testing?\n')
        print ex('status')[0]

    with g.execute('testtag', 'Mutate, Exterminate, Eliminate', 'follow-on') as ex:
        print 'test_got in', os.getcwd()
        with open('somefile.txt') as inp:
            with open('copyfile.txt','w') as out:
                out.write(inp.read())
        print ex('status')[0]
        

if __name__ == '__main__':
    test_cd()
    test_git_init()
    test_got()
