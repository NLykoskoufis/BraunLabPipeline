#!/usr/bin/env python3 

from collections import defaultdict
from sys import argv, exit
import subprocess 
import argparse
import os 


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

def check_sacct(lines):
    info = lines[1].split("|")
    if info[2] == "0:0":
        return True
    else:
        return False


def write_sacct(logFile):
    lines = get_sacct(logFile)
    exitCode = False
    if check_sacct(lines): 
        exitCode = True    
    g = open(logFile,"a")
    for l in lines: 
        g.write("__JOB_SUMMARY_INFO|"+"".join(l)+"\n")
    if exitCode:
        g.write("__JOB_SUMMARY_INFO|COMPLETED|Successfuly completed\n")
    else:
        g.write("__JOB_SUMMARY_INFO|FAILED|Failed\n")



def check_exitCodes(logFile):
    f = open(logFile, "rb")
    f.seek(-2, os.SEEK_END)
    while f.read(1) != b'\n':
        f.seek(-2, os.SEEK_CUR)
    last_line = f.readline().decode()
    line = last_line.rstrip().split("|")
    if line[0] == "__JOB_SUMMARY_INFO":
        if line[-1] == "Successfuly completed":
            return True 
        else:
            return False
        
    

if __name__ == "__main__":
        
    parser = argparse.ArgumentParser(description='Check jobs')
    parser.add_argument('-v', dest='version', action='store_true', help='Display pipeline version')
    #If user is asking for version
    if len(argv) > 1:
        if argv[1] == '-v':
            print('Pipeline version 1.00\n')
            exit(0)

    parser.add_argument('-w', '--write', dest='write_info',required=False,action="store_true", help='Write JOB ID info in log files')
    parser.add_argument('-c', '--check', dest='check_info',required=False,action="store_true", help='Check ExitCode of log files')
    parser.add_argument('-log', '--log-file', dest='logFile', type=str, help='Absolute path to logFile')
    args = parser.parse_args()
    
    if args.write_info:
        write_sacct(args.logFile)
    elif args.check_info:
        check_exitCodes(args.logFile)