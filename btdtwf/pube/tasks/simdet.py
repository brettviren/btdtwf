#!/usr/bin/env python

import sys
import pyutilib.workflow as puwf
import pyutilib.component.core as pucc

from bein import MiniLIMS, execution, program

tasks = ['simdet']

@program
def cbexe(geofile, outfile, kinurl, nevents, args=""):
    cmdstr = "cowbells.exe -n{nevents} -k {kinurl} -o {outfile} {args} {geofile}".format(**locals())
    cmd = cmdstr.split()
    print cmd
    return {'arguments': cmd, 'return_value': outfile}

class SimDet(puwf.TaskPlugin):

    pucc.alias('simdet')

    def __init__(self, *args, **kwds):
        super(SimDet, self).__init__(*args, **kwds)

        self.inputs.declare('geofile')
        self.inputs.declare('kinurl')
        self.inputs.declare('nevents')
        self.inputs.declare('cbargs')
        self.inputs.declare('lims')

        self.add_argument('--geofile', dest='geofile', type=str,
                          help='The name of the geometry configuration file.')
        self.add_argument('--kinurl', dest='kinurl', type=str,
                          help='The kinematics specification URL')
        self.add_argument('--nevents', dest='nevents', type=int, default=1,
                          help='The number of events to generate')
        self.add_argument('--cbargs', dest='cbargs', type=str, default='',
                          help='Any additional arguments to cowbells.exe')
        self.add_argument('--lims',dest='lims', type=str, default='cblims',
                          help='Set the LIMS database')

        self.outputs.declare('simfile')
        
    def execute(self):
        safeurl = self.kinurl.replace(':','_').replace('&','_').replace('/','_').replace('?','_')
        simfile = 'Simdet_with_%d_events_from_%s_with_kinematics_%s_%s.root' % \
            (self.nevents, self.geofile, safeurl, self.cbargs.replace(' ','_'))
        
        print type(simfile),simfile
        M = MiniLIMS(self.lims)
        try:
            self.simfile = M.path_to_file(simfile)
        except ValueError:
            pass
        else:
            return

        with execution(M, description = 'Produce simdet for %s' % simfile) as ex:
            geofile = ex.use(self.geofile)
            print 'Geofile is "%s" %d bytes' % (geofile, len(open(geofile).readlines()))
            cbexe(ex, geofile, 'simfile.root', self.kinurl, self.nevents, self.cbargs)
            ex.add('simfile.root', alias=simfile,
                   description = 'Simdet for %s' % simfile)

        self.simfile = simfile
        return

