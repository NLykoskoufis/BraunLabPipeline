#!/usr/bin/env python3

import sys
import glob
import re
import os

def groupCheck(groups, dir):
    test =[]
    FILES = glob.glob(f"{dir}/*.fastq.gz")
    for i in groups:
        r = re.compile("{}".format(i))
        f = list(filter(r.search,FILES))
        if len(f) != 0: 
            test.append(True)
        else:
            test.append(False)
    return all(test)

def createGroups(groups,FILES):
    groupDico = {}
    groups = groups.split("|")
    for i in groups: 
        r = re.compile("{}".format(i))
        f = list(filter(r.search,FILES))
        groupDico[i] = f
    return groupDico

