#!/usr/bin/env python3 
import subprocess
import sys 
import glob
import os
import math
import argparse
from pipeline_tools.slurmTools import catchJID
import json

pipeline_path = sys.path[0]
pipeline_tools_path = os.path.abspath(pipeline_path + "/pipeline_tools")
sys.path.append(pipeline_tools_path)
from slurmTools import *
from submitSteps import submitJobCheck


def STAR_1pass(configFileDict):
    FIRST_PASS_JID_LST = []
    
    for sample in configFileDict['sample_prefix']:
        
        outputFilePrefix = f"{sample}.1pass"
        
        MAP_CMD ="{STAR} {parameters} --outFileNamePrefix {outputFilePrefix} --genomeDir {referenceGenome}  --readFilesIn {smp}*_R1_001.fastq.gz {smp}*_R2_001.fastq.gz --readFilesCommand zcat --runThreadN 8 --outSAMtype BAM Unsorted --outSJfilterReads Unique".format(STAR = configFileDict['STAR'], parameters = configFileDict['1pass'], referenceGenome = configFileDict['reference_genome'], smp=sample, outputFilePrefix=outputFilePrefix)
        
        if '1' in configFileDict['task_list']: 
            SLURM_CMD = "{wsbatch} {slurm} -o {log_dir}/{uid}_slurm-%j.out --dependency=afterany:{JID} --wrap=\"{cmd}\"".format(wsbatch = configFileDict["wsbatch"], slurm = configFileDict["slurm_mapping"], log_dir = "{}/log".format(configFileDict['bam_dir']), uid = configFileDict["uid"], cmd = MAP_CMD, JID=configFileDict["TRIM_WAIT"])
            print(SLURM_CMD)
        else: 
            SLURM_CMD = "{wsbatch} {slurm} -o {log_dir}/{uid}_slurm-%j.out --wrap=\"{cmd}\"".format(wsbatch = configFileDict["wsbatch"], slurm = configFileDict["slurm_mapping"], log_dir = f"{configFileDict['bam_dir']}/log", uid = configFileDict["uid"], cmd = MAP_CMD)
            print(SLURM_CMD)
        
        
        out = subprocess.check_output(SLURM_CMD, shell=True, universal_newlines= True, stderr=subprocess.STDOUT)
        FIRST_PASS_JID_LST.append(catchJID(out))
        
    FIRST_PASS_WAIT = ",".join(FIRST_PASS_JID_LST)
    return FIRST_PASS_WAIT


def STAR_createTABfile(configFileDict):
    #run the perl script to merge junctions and save in raw file, then filter junctions and sort and create new junctions file that is going to be used later on. 
    
    first_pass_bam = [f"{sample}.1pass.SJ.out.tab" for sample in configFileDict['sample_prefix']]
    print(first_pass_bam)
    
    TABfile_CMD = "{perl_script} {files} > merged_junctions.txt && awk '{{if(\$6==0 && \$7 >=3) print \$0}}' | tr ' ' '\t' | sort -V -k1,1 -k2,2n > merged_junctions.unannotated.filtered3unique.txt".format(perl_script = configFileDict['junctionMerge_script'], files = " ".join(first_pass_bam))
    
    SLURM_CMD = "{wsbatch} {slurm} -o {log_dir}/{uid}_slurm-%j.out --dependency=afterany:{JID} --wrap=\"{cmd}\"".format(wsbatch = configFileDict["wsbatch"], slurm = configFileDict["slurm_general"], log_dir = "{}/log".format(configFileDict['bam_dir']), uid = configFileDict["uid"], cmd = TABfile_CMD, JID=configFileDict["FIRST_PASS_WAIT"])
    out = subprocess.check_output(SLURM_CMD, shell=True, universal_newlines= True, stderr=subprocess.STDOUT)
    
    TABFILE_WAIT = catchJID(out)
    
    return TABFILE_WAIT


read_limitSjdbInsertNsj_json(configFileDict):
    fileName = "{bam_path}/limitSjdbInsertNsj.txt".format(bam_path = configFileDict['bam_dir'])
    f = open(fileName, "rt")
    line = f.readline().rstrip().split()    
    return int(line)

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

def STAR_2pass(configFileDict):
    limitSjdbInsertNsj = read_limitSjdbInsertNsj_json(configFileDict)
    sjdbFile = configFileDict['sjdbFile']
    
    output_prefix = None 
    fastq1 = None 
    fastq2 = None 
    
    cmd = "{star} --outFileNamePrefix {outputFilePrefix} --genomeDir {STAR_genome_dir} --readFilesIn {fastq1} {fastq2}  --readFilesCommand zcat --runThreadN 8 --outSAMtype BAM SortedByCoordinate --sjdbFileChrStartEnd  {sjdbFileChrStartEnd} --outSAMunmapped Within --outSAMattributes All --outFilterMultimapNmax 20 --outSAMstrandField intronMotif --limitSjdbInsertNsj {limitSjdbInsertNsj}".format(configFileDict['STAR'], outputFilePrefix=output_prefix, STAR_genome_dir = configFileDict['reference_genome'], fastq1= fastq1, fastq2=fastq2,sjdbFileChrStartEnd=sjdbFile, limitSjdbInsertNsj=limitSjdbInsertNsj)
    return None




