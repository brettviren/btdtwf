#!/usr/bin/env python

import pyutilib.workflow as puwf
from tasks import geogen, simdet

def main():
    driver = puwf.TaskDriver()
    for task in geogen.tasks + simdet.tasks:
        driver.register_task(task)
    print driver.parse_args()
    


        
if '__main__' == __name__:
    main()
