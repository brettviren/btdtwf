#!/usr/bin/env python
'''
Interact with the bein MiniLIMS (M) or Execution object (ex) for result handling.

Results consist of a triple of:

 - name :: the process name
 - ivs :: the input value set as an ordered dict
 - ovs :: the output value set as an ordered dict

Results are identified by a SHA1 hash of the pickled tuple of (name,ivs).

'''

import pickle
import hashlib
import parameter

def result_name(procname, ivs):
    sha = hashlib.sha1()
    sha.update(pickle.dumps(ivs))
    ivs_hash = sha.hexdigest()
    fname = '%s.%s.result' % (procname, ivs_hash)
    return fname

def timestamp(M, procname, ivs):
    '''
    Return the time stamp for a prior result of process named
    <procname> with input value set <ivs> or None.
    '''
    fname = result_name(procname, ivs)
    try:
        meta = M.fetch_file(fname)
    except ValueError:
        return None
    return meta['created']

def result(M, procname, ivs):
    '''
    Return the saved output value set for the given process named
    <procname> with input value set <ivs>, or None.
    '''
    fname = result_name(procname, ivs)
    try:
        rname = M.path_to_file(fname)
    except ValueError:
        print 'result: no previous result named "%s"' % fname
        return None
    resstr = open(rname).read()
    full  = pickle.loads(resstr)
    res = full[2]
    return res


def cached(M, procname, ips):
    '''
    Return valid output value set from cache corresponding to process
    name <procname> and input parameter set <ips>, or None

    To be valid, it must exist and be newer than any files referenced
    by the input valid set.
    '''
    ivs = ips.get_values()
    last_ts = timestamp(M, procname, ivs)
    if last_ts is None: 
        print 'result.cached: no time stamp for result from process "%s"' % procname
        return None

    # Check any input files being older than result time stamp
    for name, p in ips.items():
        if p.hint != 'input':
            continue
        try:
            stat = M.fetch_file(p.value)
        except ValueError:
            print 'result.cached: no such result file for process "%s": %s' % (procname, p.value)
            return None
        this_ts = stat['created']
        if last_ts < this_ts:
            print 'result.cached: process "%s" existing result older than input file %s @ %s' % \
                (procname, p.value, this_ts)
            return None
    return result(M, procname, ivs)

def describe_ivs(procname, ivs):
    s = 'Process "%s": ' % procname
    s += ', '.join(["%s:%s"%kv for kv in ivs.items()])
    return s


def prepare(ex, procname, ips):
    '''
    Prepare the result store for an execution of the named process.
    An input parameter set is returned which is a copy of the given
    <ips> but has all input file names replaced with their name in the
    store and all output file names formatted.
    '''
    ret = parameter.ParameterSet(**ips)
    for name, p in ips.items():
        if p.hint == 'input':
            ret.replace(name, value = ex.path_to_file(p.value))
            continue
#        if p.hint == 'output':
#            ret.replace(name, value = p.value)
#            continue
    return ret
    

def finish(ex, procname, ips, ops):
    '''
    Finish an execution and store the input <ips> and output <ops>
    parameter sets associated with the process of the given <procname>.
    '''
    
    ivs = ips.get_values()
    ovs = ops.get_values()

    rname = result_name(procname, ivs)
    with open(rname, 'w') as fp:
        fp.write(pickle.dumps((procname,ivs,ovs)))

    ex.lims.delete_alias(rname)      # whether or not it exists
    print 'Adding result file %s' % rname
    ex.add(rname, alias=rname, description = describe_ivs(procname,ivs))
    
    for name, p in set(ips.items() + ops.items()):
        if not p.hint in ['input','output']:
            continue

        template='%s_{hint}_{name}_{value}'.format(name=name, **p.__dict__)
        print p,template
        #if p.hint in ['input']:
        #    print 'Associating input %s to %s' % (p.value, rname)
        #    ex.lims.associate_file(p.value, rname, template=template)
        if p.hint in ['output']:
            print 'Adding output and associating %s to %s' % (p.value, rname)
            ex.lims.delete_alias(p.value)
            ex.add(p.value, alias=p.value, description=p.desc,
                   associate_to_filename=rname, template=template)

    return

