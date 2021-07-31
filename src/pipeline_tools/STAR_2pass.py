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
    return None 

def STAR_2pass(configFileDict):
    return None 