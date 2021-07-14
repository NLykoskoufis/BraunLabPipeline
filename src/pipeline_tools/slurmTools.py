#!/usr/bin/env python3 

def catchJID(out):
    return out.rstrip().split(" ")[-1]

def getSlurmLog(log_dir, uuid, out):
    jid = catchJID(out)
    return f"{log_dir}/{uuid}_slurm-{jid}.out"


def checkJobStatus(out_list):
    return None