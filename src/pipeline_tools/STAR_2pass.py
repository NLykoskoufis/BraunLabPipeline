#!/usr/bin/env python3 


import subprocess
import sys 
import glob
import os

pipeline_path = sys.path[0]
pipeline_tools_path = os.path.abspath(pipeline_path + "/pipeline_tools")
sys.path.append(pipeline_tools_path)
from slurmTools import *


def STAR_1pass(configFileDict):
    
    return None 


def STAR_createTABfile(configFileDict):
    #run the perl script to merge junctions and save in raw file, then filter junctions and sort and create new junctions file that is going to be used later on. 
    
    cmd = "{perl_script} {files} > merged_junctions.txt && awk '{{if(\$6==0 && \$7 >=3) print \$0}}' | tr ' ' '\t' | sort -V -k1,1 -k2,2n > merged_junctions.unannotated.filtered3unique.txt"
    
    return None
 
def get_limitSjdbInsertNsj(configFileDict):
    cmd = "wc -l {file}/merged_junctions.unannotated.filtered3unique.txt".format(configFileDict['bam_dir'])
    out = int(subprocess.check_output(cmd, shell=True, universal_newlines=True, stderr= subprocess.STDOUT)[0])
    return out

def STAR_2pass(configFileDict):
    return None

