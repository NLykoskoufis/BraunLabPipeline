#!/usr/bin/env python3 

import subprocess
import sys 
import glob
import os
import math
import argparse



def get_limitSjdbInsertNsj(file):
    cmd = f"wc -l {file}/merged_junctions.txt"
    out = int(subprocess.check_output(cmd, shell=True, universal_newlines=True, stderr= subprocess.STDOUT).split()[0])
    return out

def increase_limitSjdbInsertNsj(value):
    value = str(value)
    len_val = len(value)
    new_number = []
    if len_val > 1:
        new_number.append(value[0])
        new_number.append(str(int(value[1])+1))
        for i in range(2,len_val):
            new_number.append(str(0))
    else:
        new_number.append(str(int(value)+1))
    return new_number

if __name__ == "__main__":
    print("fuck")