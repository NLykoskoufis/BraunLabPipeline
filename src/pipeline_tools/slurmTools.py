#!/usr/bin/env python3 

import subprocess

def catchJID(out):
    return out.rstrip().split(" ")[-1]

def getSlurmLog(log_dir, uuid, out):
    jid = catchJID(out)
    return f"{log_dir}/{uuid}_slurm-{jid}.out"


def submitJobCheck(configFileDict, log_key, wait_key):
    log_files = configFileDict[log_key]
    for file in log_files:
        CMD = "python3 {bin} append -log {input}".format(bin=configFileDict['jobCheck'], input=file)
        SLURM_CMD = "{wsbatch} --dependency=afterany:{JID} --wrap=\"{cmd}\"".format(wsbatch=configFileDict['wsbatch'], cmd=CMD, JID=wait_key)
        out = subprocess.check_output(SLURM_CMD, shell=True, universal_newlines=True, stderr=subprocess.STDOUT)
        