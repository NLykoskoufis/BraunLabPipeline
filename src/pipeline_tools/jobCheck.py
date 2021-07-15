#!/usr/bin/env python3 

from sys import argv 
import subprocess 

def get_sacct(logFile):
    f = open(logFile,"rt")
    line = f.readline().rstrip().split(" ")
    if line[0].split("_")[2] != "WSBATCH":
        raise Exception("You did not run your job using wsbatch. Impossible to retrieve exitCode of script")
    jobID = line[0].split("_")[-1]
    cmd = "sacct -j {jobID} -oJobID,state,exitcode,MaxRSS,Start,End,Elapsed,NNodes,NodeList -P".format(jobID=jobID)
    
    out = subprocess.check_output(cmd, shell=True, universal_newlines=True, stderr=subprocess.STDOUT)
    lines = out.split("\n")
    return lines 

def check_sacct(logFile):
    lines = get_sacct(logFile)
    info = lines[1].split("|")
    if info[2] == "0:0":
        return True
    else:
        return False


def write_sacct(logFile):
    lines = get_sacct(logFile)
    
    g = open(logFile,"a")
    for l in lines: 
        g.write("__JOB_SUMMARY_INFO|"+"".join(l)+"\n")

if __name__ == "__main__":
    write_sacct(*argv[1:])