#!/usr/bin/env python
'''
Test a celery based work flow

  $ celery -A test_celery worker --loglevel=debug -n 4

  $ ipython
  In [1]: import test_celery as tc
  In [2]: tc.test_root()
  In [3]: a = [(tc.make_hist.s(infile='foo.root') | tc.do_print.s(outfile='foo%d.pdf'%n)).apply_async() for n in range(10)]

'''

from celery import Celery

celery = Celery('tasks', backend='amqp', broker='amqp://guest@localhost//')
import ROOT


@celery.task
def add(x, y):
    return x + y

@celery.task
def make_hist(infile, treename = 'cowbells', what='hc.t', cuts=''):
    fp = ROOT.TFile.Open(infile)
    tree = fp.Get(treename)
    h = ROOT.TH1F("h",what,400,0,40)
    tree.Draw('%s>>%s' % (what,h.GetName()), cuts, 'goff')
    return h

@celery.task
def do_print(hist, outfile='foo.pdf', gopts = ''):
    canvas = ROOT.TCanvas('canvas','canvas',500,500)
    hist.Draw(gopts)
    canvas.Print(outfile, 'pdf')
    return outfile

def test_add(x=1,y=2):
    a = (add.s(x,2) | add.s(y)).apply_async()
    print a
    print a.get()

def test_root(infile='foo.root', outfile='foo.pdf'):
    a = (make_hist.s(infile=infile) | do_print.s(outfile=outfile)).apply_async()
    print a
    print a.get()
