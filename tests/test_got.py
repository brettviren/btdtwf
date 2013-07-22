#!/usr/bin/env python

import os
from btdtwf import got, util
        
def test_cd():
    print os.getcwd()
    with util.cd('/tmp') as oldir:
        print oldir
        print os.getcwd()
    print os.getcwd()

def test_make_git():
    git = got.Git('/tmp/got')
    try:
        print git('status')
    except got.GitError:
        print 'Got expected git error'
    else:
        raise ValueError,'Did not get expected git error, did /tmp/got already exist?'


def test_got(num=1):
    g = got.Got('/tmp/got')
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
