#!/usr/bin/env python3 

from os import wait
import subprocess
import sys 



def catchJID(out):
    return out.rstrip().split(" ")[-1]

def getSlurmLog(log_dir, uuid, out):
    jid = catchJID(out)
    return f"{log_dir}/{uuid}_slurm-{jid}.out"



        

    

    
    

