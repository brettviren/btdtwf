#!/usr/bin/env python
'''
'''

import pyutilib.workflow
import bein

import result


class ProcessTask(pyutilib.workflow.Task):
    def __init__(self, name, callable, input_param_set, output_param_set,
                 *args, **kwds):
        super(ProcessTask, self).__init__(*args, name=name, **kwds)
        self.callable = callable

        self.ops = output_param_set
        self.ips = input_param_set

        self.inputs.declare('provenance_name', default='', doc='Name of provenance tracking database')

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

        return

    def M(self):
        if not self.provenance_name: 
            return None
        return bein.MiniLIMS(self.provenance_name)
        

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
        # Set workflow ports
        for name, p in self.ops.items():
            setattr(self, name, p.value)
        for name in self.to_shunt:
            out_name = 'out_' + name
            value = self.ips[name].value
            setattr(self, out_name, value)
            ovs[out_name] = value
            #print 'SHUNT: "%s": "%s" -> "%s" = "%s"' % (self.name, name, out_name, value)
        self.ops.set_values(**ovs)
        #print 'OUTPUTS "%s": %s' % (self.name, self.ops)

    def execute(self):
        print 'EXECUTE "%s"' % self.name
        self.get_inputs()

        ovs = result.cached(self.M(), self.name, self.ips)
        if ovs is not None:
            print 'CACHED result: "%s"' % str(ovs)
            self.set_outputs(ovs)
            return

        print 'RUNNING "%s"' % self.name
        with bein.execution(self.M()) as ex:
            stored_ips = result.prepare(ex, self.name, self.ips)
            stored_ivs = stored_ips.get_values()
            ovs = self.callable(ex, **stored_ivs)
            if ovs is None: ovs = dict()
            self.set_outputs(ovs)
            result.finish(ex, self.name, self.ips, self.ops)
        return

tasks = dict()
def register(name, callable, input_param_set, output_param_set, *args, **kwds):
    global tasks
    t = ProcessTask(name,callable,input_param_set,output_param_set,*args,**kwds)    
    tasks[name] = t
    return t

