#!/usr/bin/env python3 

import subprocess
import sys 
import os 
import time 
import argparse
from collections import defaultdict
import uuid
import glob

pipeline_path = sys.path[0]
pipeline_tools_path = os.path.abspath(pipeline_path + "/pipeline_tools")

sys.path.append(pipeline_tools_path)
from writeEmail import writeEmail
from configParser import getConfigDict
from fastqTools import getFastqPrefix
from slurmTools import catchJID

# ===========================================================================================================
DESC_COMMENT = "ATACseq pipeline"
SCRIPT_NAME = "main.py"
# ===========================================================================================================

"""
#===============================================================================
@author: Nikolaos Lykoskoufis
@date: 7th of July
@copyright: Copyright 2021, University of Geneva
ATACseq pipeline for mapping, peak calling, etc
#===============================================================================
"""


"""
#===============================================================================
###### STEPS PERFORMED BY PIPELINE ######

1. TRIM reads
2. MAP reads to reference genome ==> Wait for 1 is 1 is needed to run
3. FILTER unmapped, low QUAL and chrM + sortBAM ==> WAIT FOR 2
4. Mark PCR duplicates ==> WAIT FOR 3
5. REMOVE PCR duplicates, vendor QUAL control and secondary alignment ==> WAIT FOR 4
6. INDEX BAM ==> WAIT FOR 5
7. CREATE .bw for visualization <INDEPENDENT STEP FROM 8,9,10> => ONLY NEED TO WAIT FOR 6 TO BE DONE. 
8. CONVERT bam2bed ==> Wait for 6 to be done
9. Bed file with extended reads ==> Wait for 8
10. PEAK Calling ==> Wait for 9
#===============================================================================
"""


parser = argparse.ArgumentParser(description='Pipeline to process data from illumina sequencers.')
parser.add_argument('-v', dest='version', action='store_true', help='Display pipeline version')
#If user is asking for version
if len(sys.argv) > 1:
    if sys.argv[1] == '-v':
        print('Pipeline version 1.00\n')
        sys.exit(0)

parser.add_argument('-fastq', '-fastqdir', dest='fastq_dir', type=str, help='Absolut path fastq to diretor(y)ies. If multiple directories, separate eache path with space')
parser.add_argument('-bam', '-bamdir', dest='bam_dir', type=str, help='Path bam diretory, is multiple, separate with space.')
parser.add_argument('-sortedBam', dest='sorted_bam_dir', type=str, help='Path to sorted bam directory, if not set, first bam directory is used.')
parser.add_argument('-eqd', '-quantification_dir', dest='eq_dir', type=str, help='Absolut path peak calling diretory')
parser.add_argument('-od', '-outputdir', dest='output_dir', type=str, help='Path to output directory')
parser.add_argument('-cf', dest='config_file_path', required=True,type=str, help='Name of your configuration file: project_run_config_V1')
parser.add_argument('-tf', dest='tar_fastq', action='store_true', help='True if you want to do a backup of fastq files. \'-rn\' and \'-pn\' options are mandatory to do a backup.')
parser.add_argument('-tb', dest='tar_bam', action='store_true', help='True if you want to do a backup of bam files. \'-rn\' and \'-pn\' options are mandatory to do a backup.')
parser.add_argument('-t', dest='task', type=str, required=True, nargs='+', help='')

####################
#    CHECK ARGS    #
####################

#Get command line args
args = parser.parse_args()

####### STEP 1 ########
# Initialize pipeline and check which steps should be ran.


#Get command line args
args = parser.parse_args()

#get list of tasks
if not args.task:
    sys.stderr.write('ERROR: You must give task(s) to run : arg -t\n')
    sys.exit(1)
task_list = args.task
if 'all' in task_list:
    task_list = ['1','2','3','4','5','6','7','8','9','10']
    
if not args.config_file_path:
    sys.stderr.write('ERROR: You must provide a configuration file to run the pipeline : arg -cf\n')
    sys.exit(1)
elif not os.path.exists(args.config_file_path):
    sys.stderr.write('ERROR: The configuration file you provided does not exist')
    sys.exit(1)
else:
    configFileDict = getConfigDict(args.config_file_path) # Create dictionay containing all important information for the pipeline to work. 
     
#Create unique ID for the run
configFileDict["uid"] = (str(uuid.uuid1())[:8])

# Add extra information to the dictionary
configFileDict["pipeline_path"] = pipeline_path
configFileDict["raw_dir"] = args.output_dir
configFileDict["bam_dir"] = args.bam_dir
configFileDict["fastq_dir"] = args.fastq_dir
configFileDict["quantification_dir"] = args.eq_dir

 





########################
##### START TASKS ###### 
########################

print(" * Starting\n")
print(f" * Unique ID of this run: {str(configFileDict['uid'])}\n")


# ===========================================================================================================
STEP1 = "Trimming reads"
# ===========================================================================================================

if '1' in task_list: 
    print("Running trimming of reads.\n")
    if not os.path.isdir(args.fastq_dir): 
        sys.stder("ERROR. The fastq directory does not exist.")
    else: 
        trimmed_fastq_dir = f"{args.output_dir}/trimmed_fastq"
        configFileDict['trimmed_fastq_dir'] = trimmed_fastq_dir 
        if os.path.isdir(trimmed_fastq_dir):
            sys.stderr("ERROR. The directory already exists! Exiting to avoid overwriting files")
        else: 
            os.mkdir(trimmed_fastq_dir)
            os.mkdir(f"{trimmed_fastq_dir}/log")
            
            # Create list with JOBIDs of trimming. This is important because it allows for the rest of the submitted jobs to wait for this. 
            TRIM_JID_LIST = []
            FASTQ_FILES = getFastqPrefix(args.fastq_dir)
            for file in FASTQ_FILES:
                TRIM_CMD = "{bin} {parameters} -o {trimmed_dir}/{file}_R1_001.trim.fastq.gz -p {trimmed_dir}/{file}_R2_001.trim.fastq.gz {fastq_dir}/{file}_R1_001.fastq.gz {fastq_dir}/{file}_R2_001.fastq.gz".format(bin=configFileDict["cutadapt"], parameters=configFileDict["trim_reads"], file=file, trimmed_dir = trimmed_fastq_dir, fastq_dir=args.fastq_dir)
                SLURM_CMD = "{wsbatch} {slurm} -o {trimmed_log_dir}/{uid}_slurm-%j.out --wrap=\"{cmd}\"".format(wsbatch = configFileDict["wsbatch"], slurm = configFileDict["slurm_trim"], trimmed_log_dir = f"{trimmed_fastq_dir}/log", uid = configFileDict["uid"], cmd = TRIM_CMD)
                print(SLURM_CMD)
                out = subprocess.check_output(SLURM_CMD, shell=True, universal_newlines= True, stderr=subprocess.STDOUT)
                TRIM_JID_LIST.append(catchJID(out))
                #TRIM_JID_LIST.append('0') #### FOR DEBUGGING PURPOSES
                
    TRIM_WAIT = ",".join(TRIM_JID_LIST)
    del TRIM_JID_LIST

                     
# ===========================================================================================================
STEP2 = "Mapping reads"
# ===========================================================================================================
                
if '2' in task_list: 
    print("Running mapping of reads.\n")
    if not os.path.isdir(trimmed_fastq_dir): 
        sys.stder("ERROR. The trimmed fastq directory does not exist.")
    else: 
        bam_dir = f"{args.output_dir}/bam"
        configFileDict['bam_dir'] = bam_dir
        if os.path.isdir(bam_dir):
            sys.stderr("ERROR. The directory already exists! Exiting to avoid overwriting files")
        else: 
            os.mkdir(bam_dir)
            os.mkdir(f"{bam_dir}/log")
            
            # Create list with JOBIDs of trimming. This is important because it allows for the rest of the submitted jobs to wait for this. 
            MAP_JID_LIST = []
            FASTQ_FILES = getFastqPrefix(args.fastq_dir)
            
            if configFileDict["mapper"] == "bowtie2":
                bowtie_params = configFileDict['bowtie_parameters']
                map_bin = configFileDict['bowtie2']
                
            for file in FASTQ_FILES:
                #bowtie2 -p 8 -x $mm10 --maxins 2000 -N 1 -1 testFile_R1_001.trim.fastq.gz -2 testFile_R2_001.trim.fastq.gz -S testFile.sam                                                         
                
                MAP_CMD = "{mapper} {parameters} -1 {dir}/{file}_R1_001.trim.fastq.gz -2 {dir}/{file}_R2_001.trim.fastq.gz | {samtools} -b -h -o {bam_dir}/{file}.bam".format(mapper=map_bin, parameters=bowtie_params,dir=trimmed_fastq_dir,file=file, samtools = configFileDict["samtools"], bam_dir=bam_dir)
                if '1' in task_list: 
                    SLURM_CMD = "{wsbatch} {slurm} -o {log_dir}/{uid}_slurm-%j.out --dependency=afterok:{JID} --wrap=\"{cmd}\"".format(wsbatch = configFileDict["wsbatch"], slurm = configFileDict["slurm_mapping"], log_dir = f"{bam_dir}/log", uid = configFileDict["uid"], cmd = MAP_CMD, JID=TRIM_WAIT)
                    print(SLURM_CMD)
                else: 
                    SLURM_CMD = "{wsbatch} {slurm} -o {log_dir}/{uid}_slurm-%j.out --wrap=\"{cmd}\"".format(wsbatch = configFileDict["wsbatch"], slurm = configFileDict["slurm_mapping"], log_dir = f"{bam_dir}/log", uid = configFileDict["uid"], cmd = MAP_CMD)
                    print(SLURM_CMD)
                out = subprocess.check_output(SLURM_CMD, shell=True, universal_newlines= True, stderr=subprocess.STDOUT)
                MAP_JID_LIST.append(catchJID(out))
                #MAP_JID_LIST.append('0')
                
    MAP_WAIT = ",".join(MAP_JID_LIST)
    del MAP_JID_LIST

if '3' in task_list: 
    print(" * Running filtering and sorting of BAM files\n")
    sorted_bam_dir = f"{args.output_dir}/sorted_bam"
    bam_dir = f"{args.output_dir}/bam"
    if not os.path.isdir(bam_dir):
        sys.stderr("ERROR! The bam directory does not exist.")
    elif os.path.isdir(sorted_bam_dir): 
        sys.stderr("ERROR! The sorted bam directory already exist.")
    else: 
        os.mkdir(sorted_bam_dir)
        os.mkdir(f"{sorted_bam_dir}/log")
        
        BAM_FILTER_JID_LIST = []
        BAM_FILES = glob.glob(f"{bam_dir}/*.bam")
        
        for bam in BAM_FILES: 
            OUTPUT_FILE = os.path.basename(bam).replace(".bam",".QualTrimNoMt.bam")
            print(OUTPUT_FILE)
            
            FILTER_CMD = "{samtools} view {parameters} | awk '{{if(\$3!~/chr[MT]/) {{print}}}}' | {samtools} sort -O BAM -T {bam_dir}/{file} -o {sorted_bam_dir}/{output}".format(samtools=configFileDict["samtools"], parameters=configFileDict['filter_bam'], bam_dir=bam_dir, file=bam, sorted_bam_dir=sorted_bam_dir, output=OUTPUT_FILE)
            print(FILTER_CMD)
            
            if '2' in task_list: 
                SLURM_CMD = "{wsbatch} {slurm} -o {log_dir}/{uid}_slurm-%j.out --dependency=afterok:{JID} --wrap=\"{cmd}\"".format(wsbatch = configFileDict["wsbatch"], slurm = configFileDict["slurm_general"], log_dir = f"{sorted_bam_dir}/log", uid = configFileDict["uid"], cmd = FILTER_CMD, JID=MAP_WAIT)
            else: 
                SLURM_CMD = "{wsbatch} {slurm} -o {log_dir}/{uid}_slurm-%j.out --wrap=\"{cmd}\"".format(wsbatch = configFileDict["wsbatch"], slurm = configFileDict["slurm_general"], log_dir = f"{sorted_bam_dir}/log", uid = configFileDict["uid"], cmd = FILTER_CMD)
            out = subprocess.check_output(SLURM_CMD, shell=True, universal_newlines= True, stderr=subprocess.STDOUT)
            BAM_FILTER_JID_LIST.append(catchJID(out))
    FILTER_BAM_WAIT = ",".join(BAM_FILTER_JID_LIST)
    del BAM_FILTER_JID_LIST



                
            
            
