#!/usr/bin/env python3 

import os 
import sys

def checkDir(path):
    return os.path.isdir(path)



def createLog(path, dryRun=False):
    if dryRun:
        print(f"os.mkdir(\"{path}/log)\"")
    else: 
        try:
            os.mkdir(f"{path}/log")
        except FileExistsError: 
            print("ERROR. The directory already exist. To avoid overwriting or erasing data, the pipeline cannot continue. Please either specify another directory or erase the directory before running the pipeline.")
            sys.exit(1)



def createDir(path, dryRun=False):
    if dryRun: 
        print(f"os.mkdir(\"{path})\"")
    else:
        try:
            os.mkdir(path)
        except FileExistsError: 
            print("ERROR. The directory already exist. To avoid overwriting or erasing data, the pipeline cannot continue. Please either specify another directory or erase the directory before running the pipeline.")
            sys.exit(1)

