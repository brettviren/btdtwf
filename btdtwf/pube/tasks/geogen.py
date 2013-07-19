#!/usr/bin/env python

import sys
import pyutilib.workflow as puwf
import pyutilib.component.core as pucc

from bein import MiniLIMS, execution

from cowbells import geom, default
default.all()


def params2kwds(param):
    if not param: return dict()
    return {k:v for k,v in [kv.split('=') for kv in param.split(',')]}

tasks = ['gengeo']

class GenGeo(puwf.TaskPlugin):

    pucc.alias('gengeo')

    def __init__(self, *args, **kwds):
        super(GenGeo, self).__init__(*args, **kwds)
        
        self.inputs.declare('detector')
        self.inputs.declare('param')
        self.inputs.declare('lims')
        self.add_argument('--detector',dest='detector', type=str,
                          help='Name the detector setup')
        self.add_argument('--param',dest='param', type=str, default="",
                          help='Comma separated key=value pairs of parameters')
        self.add_argument('--lims',dest='lims', type=str, default='cblims',
                          help='Set the LIMS database')
        
        self.outputs.declare('geofile')

    def gen(self, **kwds):
        print 'Generating for "%s"' % self.detector
        modname = 'cowbells.builder.%s' % self.detector
        exec ('import %s' % modname)
        mod = sys.modules[modname]
        print mod
        b = mod.Builder(**kwds)
        worldv = b.top()
        geom.placements.PhysicalVolume('pvWorld',worldv)
        b.place()
        b.sensitive()

    def execute(self):
        fname = '%s_%s.json' % (self.detector, self.param or "defaults")
        
        M = MiniLIMS(self.lims)
        try:
            self.geofile = M.path_to_file(fname)
        except ValueError:
            pass
        else:
            return

        with execution(M, description = 'Produce geometry description for %s' % fname) as ex:
            kwds = params2kwds(self.param)
            self.gen(**kwds)
            with open(fname, 'w') as fp:
                fp.write(geom.dumps_json())
                fp.close
            ex.add(fname, alias=fname, 
                   description = 'Detector %s with params %s' % (self.detector, self.param))
            
        self.geofile = M.path_to_file(fname)
        return
        

        
if '__main__' == __name__:
    driver = puwf.TaskDriver()
    for task in tasks:
        driver.register_task(task)
    print driver.parse_args()
