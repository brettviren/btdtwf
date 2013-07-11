#!/usr/bin/env python
'''
'''

from collections import OrderedDict
import pyutilib.workflow
from bein import execution

import result, parameter


tasks = dict()

class ProcessTask(pyutilib.workflow.Task):
    def __init__(self, minilims, name, callable, input_param_set, output_param_set,
                 *args, **kwds):
        super(ProcessTask, self).__init__(*args, name=name, **kwds)
        self.M = minilims
        self.callable = callable

        self.ops = output_param_set
        self.ips = input_param_set

        self.to_shunt = list()
        # Declare task ports
        for name, p in self.ops.items():
            self.outputs.declare(name, default=p.value, doc=p.desc)
        for name, p in self.ips.items():
            self.inputs.declare(name, default=p.value, doc=p.desc)

            if p.hint == 'output':
                out_name = 'out_'+name
                if not out_name in self.ops.keys():
                    self.outputs.declare(out_name, default=p.value, doc=p.desc)
                    self.to_shunt.append(name)

        global tasks
        tasks[name] = self
        return

    def get_inputs(self):
        'Set input parameters based on current workflow inputs'
        ivs = {name:getattr(self, name) for name in self.ips.keys()}
        # one more time to format any file names
        for name, p in self.ips.items():
            if p.hint in ['input', 'output']:
                #print 'get_inputs(%s,%s,%s) with %s' % (self.name, name, ivs[name], ivs)
                ivs[name] = ivs[name].format(**ivs)
        self.ips.set_values(**ivs)
        #print 'INPUTS "%s": %s' % (self.name, self.ips)
            
    def set_outputs(self, ovs):
        'Apply the output value set to the current workflow output values and output parameters'
        self.ops.set_values(**ovs)
        # Set workflow ports
        for name, p in self.ops.items():
            setattr(self, name, p.value)
        for name in self.to_shunt:
            out_name = 'out_' + name
            value = self.ips[name].value
            setattr(self, out_name, value)
            #print 'SHUNT: "%s": "%s" -> "%s" = "%s"' % (self.name, name, out_name, value)
        #print 'OUTPUTS "%s": %s' % (self.name, self.ops)

    def execute(self):
        print 'EXECUTE "%s"' % self.name
        self.get_inputs()

        ovs = result.cached(self.M, self.name, self.ips)
        if ovs:
            self.set_outputs(ovs)
            return

        with execution(self.M) as ex:
            stored_ips = result.prepare(ex, self.name, self.ips)
            stored_ivs = stored_ips.get_values()
            ovs = self.callable(ex, **stored_ivs)
            self.set_outputs(ovs)
            result.finish(ex, self.name, self.ips, self.ops)
        return
