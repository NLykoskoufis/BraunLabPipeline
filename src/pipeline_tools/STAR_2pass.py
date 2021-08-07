#!/usr/bin/env python3 


import subprocess
import sys 
import glob
import os
import math

pipeline_path = sys.path[0]
pipeline_tools_path = os.path.abspath(pipeline_path + "/pipeline_tools")
sys.path.append(pipeline_tools_path)
from slurmTools import *


def STAR_1pass(configFileDict):
    outputFilePrefix = None 
    fastq1 = None 
    fastq2 = None 
    
    cmd ="{STAR} {parameters} --outFileNamePrefix {outputFilePrefix} --genomeDir {referenceGenome}  --readFilesIn {fastq1} {fastq2} --readFilesCommand zcat --runThreadN 8 --outSAMtype BAM Unsorted --outSJfilterReads Unique".format(STAR = configFileDict['STAR'], parameters = configFileDict['1pass'], referenceGenome = configFileDict['reference_genome'], fastq1=fastq1, fastq2=fastq2, outputFilePrefix=outputFilePrefix)
    return None 


def STAR_createTABfile(configFileDict):
    #run the perl script to merge junctions and save in raw file, then filter junctions and sort and create new junctions file that is going to be used later on. 
    
    cmd = "{perl_script} {files} > merged_junctions.txt && awk '{{if(\$6==0 && \$7 >=3) print \$0}}' | tr ' ' '\t' | sort -V -k1,1 -k2,2n > merged_junctions.unannotated.filtered3unique.txt"
    
    return None
 
def get_limitSjdbInsertNsj(configFileDict):
    cmd = "wc -l {file}/merged_junctions.txt".format(configFileDict['bam_dir'])
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

def STAR_2pass(configFileDict):
    limitSjdbInsertNsj = increase_limitSjdbInsertNsj(get_limitSjdbInsertNsj(configFileDict))
    output_prefix = None 
    fastq1 = None 
    fastq2 = None 
    
    cmd = "{star} --outFileNamePrefix {outputFilePrefix} --genomeDir {STAR_genome_dir} --readFilesIn {fastq1} {fastq2}  --readFilesCommand zcat --runThreadN 8 --outSAMtype BAM SortedByCoordinate --sjdbFileChrStartEnd  {sjdbFileChrStartEnd} --outSAMunmapped Within --outSAMattributes All --outFilterMultimapNmax 20 --outSAMstrandField intronMotif --limitSjdbInsertNsj {limitSjdbInsertNsj}".format(configFileDict['STAR'], outputFilePrefix=output_prefix, STAR_genome_dir = configFileDict['reference_genome'], fastq1= fastq1, fastq2=fastq2,sjdbFileChrStartEnd=sjdbFile, limitSjdbInsertNsj=limitSjdbInsertNsj)
    return None

