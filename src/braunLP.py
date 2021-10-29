#!/usr/bin/env python3 
from __future__ import print_function
import subprocess
import sys 
import os
from pathlib import Path
import time 
import argparse
from collections import defaultdict
import uuid
import glob
from datetime import datetime
import json
from rich.progress import Progress

pipeline_path = sys.path[0]
pipeline_tools_path = os.path.abspath(pipeline_path + "/pipeline_tools")
utils_tools_path = os.path.abspath(pipeline_path+"/utils")
scripts_path = os.path.abspath(pipeline_path+"/scripts")
sys.path.append(pipeline_tools_path)
sys.path.append(utils_tools_path)
sys.path.append(scripts_path)
from writeEmail import writeEmail
from configParser import getConfigDict, dict2File
from fastqTools import getFastqPrefix
from slurmTools import *
from dirCheck import * 
from submitSteps import *
from verbose import verbose as vrb


# ===========================================================================================================
DESC_COMMENT = "BraunLabPipeline"
SCRIPT_NAME = "main.py"
# ===========================================================================================================

"""
#===============================================================================
@author: Nikolaos Lykoskoufis
@date: 7th of July
@copyright: Copyright 2021, University of Geneva
Pipeline for Processing ATACseq, ChIP-seq and RNAseq data
#===============================================================================
"""

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


parser = argparse.ArgumentParser(description='''
BraunLabPipeline
 *  Authors     : Nikolaos Lykoskoufis / Simon Braun  
 *  Contact     : nikolaos.lykoskoufis@unige.ch / simon.braun@unige.ch  
 *  Webpage     : https://github.com/NLykoskoufis/braunATACpipeline 
 *  Version     : 1.0
 *  Description : Pipeline to process High throughput sequencing data.''',formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-v', dest='version', action='store_true', help='Display pipeline version')
#If user is asking for version
if len(sys.argv) > 1:
    if sys.argv[1] == '-v':
        print('Pipeline version 1.00\n### BETA VERSION. USE IT WITH CAUTION!!!')
        sys.exit(0)

parser.add_argument('-raw', '--raw-dir', dest='raw_dir',required=True, type=str, help='Absolute path to the raw directory')
parser.add_argument('-fastq', '--fastq-dir', dest='fastq_dir', type=str, help='Absolut path fastq to diretor(y)ies. If multiple directories, separate eache path with space')
#parser.add_argument('-trimfastq', '--trim-fastq-dir', dest='trimmed_fastq_dir', type=str, help='Absolut path trimmed fastq to diretor(y)ies. If multiple directories, separate eache path with space')
parser.add_argument('-bam', '--bam-dir', dest='bam_dir', type=str, help='Path bam diretory, is multiple, separate with space.')
parser.add_argument('-peak', '--peak-dir', dest='peaks_dir', type=str, help='Path peak diretory, is multiple, separate with space.')

#parser.add_argument('-sortedBam','--sorted-bam-dir', dest='sorted_bam_dir', type=str, help='Path to sorted bam directory, if not set, first bam directory is used.')
parser.add_argument('-eqd','--quant-dir', '-quantification_dir', dest='eq_dir', type=str, help='Absolut path quantifications diretory')
parser.add_argument('-bed', '--bed-dir', dest='bed_dir', type=str, help='Absolut path of where to save/read bed files')
parser.add_argument('-bw', '--bigwig-dir', dest='bigwig_dir', type=str, help='Absolut path peak calling diretory')
parser.add_argument('-od', '--output-dir', dest='output_dir', type=str, help='Path to output directory. Use it only if you do not run the pipeline from step')
parser.add_argument('-cf','--configuration-file', dest='config_file_path', required=True,type=str, help='Name of your configuration file: project_run_config_V1')
#parser.add_argument('-tf', dest='tar_fastq', action='store_true', help='True if you want to do a backup of fastq files. \'-tf_dir\' option is mandatory to do a backup of fastq files.')
#parser.add_argument('-tb', dest='tar_bam', action='store_true', help='True if you want to do a backup of bam files. \'-tb_dir\' option is mandatory to do a backup of bam files.')
#parser.add_argument('-tf_dir', '--tf-dir', dest='backup_fastq_dir', type=str, help='Path to backup fastq diretory. This option is required if you want to perform a backup of fastq files.')
#parser.add_argument('-tb_dir', '--tb-dir', dest='backup_bam_dir', type=str, help='Path to backup bam diretory. This option in required if you want to perform a backup of bam files.')
parser.add_argument('-t','--task', dest='task', type=str, required=True, nargs='+', help='')


####################
#    CHECK ARGS    #
####################

#Get command line args
args = parser.parse_args()

if not args.config_file_path:
    sys.stderr.write('ERROR: You must provide a configuration file to run the pipeline : arg -cf\n')
    sys.exit(1)
elif not os.path.exists(args.config_file_path):
    sys.stderr.write('ERROR: The configuration file you provided does not exist')
    sys.exit(1)
else:
    configFileDict = getConfigDict(args.config_file_path) # Create dictionay containing all important information for the pipeline to work. 


"""
#================================
## HARDCODED PATHS TO SCRIPTS ##
#================================
"""


configFileDict['mail_script'] = f"{pipeline_tools_path}/sendEmail.py"
configFileDict['jobCheck'] = f"{pipeline_tools_path}/jobCheck.py"
configFileDict['report'] = f"{pipeline_tools_path}/reportCreator.py"
configFileDict['junctionMerge_script'] = f"{scripts_path}/merge_junctions.pl"
configFileDict['extendReadsScript'] = f"{scripts_path}/extendBedReads.sh"
configFileDict['ATACseqQC'] = f"{scripts_path}/fragmentSizeDist.R"
configFileDict['ATACbamQC'] = f"{scripts_path}/atacQC_stats.R"
configFileDict['bam2bed_script'] = f"{scripts_path}/bam2bed.sh"
configFileDict['zipDirectoryScript'] = f"{pipeline_tools_path}/zipDirectory.py"

# Python3 softwares. This assumes that the libraries were installed using pip3 install <software> --user 
configFileDict['cutadapt'] = f"{str(Path.home())}/.local/bin/cutadapt"
configFileDict['multiQC'] = f"{str(Path.home())}/.local/bin/multiqc"



#get list of tasks
if not args.task:
    vrb.error('ERROR: You must give task(s) to run : arg -t\n')
    sys.exit(1)
task_list = args.task
if configFileDict['technology'] == "ATACseq":
    if 'all' in task_list:
        task_list = ['1','1.1','2','3','4','4.1','4.2','5','6','7','8','8.1']
elif configFileDict['technology'] == "ChIPseq":
    if 'all' in task_list: 
        task_list = ['1','1.1','2','3','4','4.2','5','6','7','8','8.1'] # TO BE CONFIRMED
elif configFileDict['technology'] == "RNAseq":
    if 'all' in task_list: 
        task_list = ['1.1', '2', '9']
    if '3' in task_list or '4' in task_list: 
        vrb.warning("WARNING!!! It is not recommended to remove duplicated reads for RNAseq experiments as you may kill your signal for very highly expressed genes.")
    if '8' in task_list:
        vrb.error("ERROR. You cannot call peaks from RNAseq data.")
    if '5' in task_list or '6' in task_list or '7' in task_list:
        vrb.warning("WARNING! These are not RNAseq data specific steps.")
else: 
    vrb.error("ERROR. The pipeline can only process ATACseq, ChIPseq or RNAseq data. PLease specify one of them in the configuration file")

task_list.append("report") # No matter what step you are running, always create a report!

if not args.raw_dir: 
    vrb.error("ERROR. You need to specify a raw directory for the pipeline to work")
else: 
    configFileDict['raw_dir'] = args.raw_dir
    configFileDict['raw_log'] = f"{args.raw_dir}/log"

if args.raw_dir and not args.output_dir: 
    print("The raw directory is also the output directory")
if args.raw_dir and args.output_dir: 
    print("Results will be written in the output directory specified and not the raw directory")
    configFileDict['raw_log'] = f"{args.output_dir}/log"
if args.raw_dir == args.output_dir:
    vrb.error("ERROR. The raw directory and output directories are the same. Either specify a different output directory than the raw directory or do not specify at all.")

#Create unique ID for the run
configFileDict["uid"] = (str(uuid.uuid1())[:8])

# Add extra information to the dictionary
configFileDict["pipeline_path"] = pipeline_path

### WHICH STEPS ARE GOING TO BE RAN AND CHECK WHETHER ALL DIRECTORIES WERE GIVEN 
configFileDict['task_list'] = task_list 


###### OUTPUTING PARAMETERS USED AND TASKS SELECTED TO RUN ########

print(f"//=========================={bcolors.BOLD} Pipeline Settings {bcolors.ENDC} ==========================\\\\")
print("||")

print(f"||    * Processing {bcolors.OKCYAN}{bcolors.BOLD}{configFileDict['technology']}{bcolors.ENDC} data")
if args.task == "all":
    print("||    * Running all tasks:", " ".join(task_list))
else:
    print("||    * Running tasks:", " ".join(task_list))

print(f"||    * {bcolors.BOLD}configuration file{bcolors.ENDC}: [{args.config_file_path}]")
print(f"||    * {bcolors.BOLD}raw dir{bcolors.ENDC}: [{args.raw_dir}]")

if args.output_dir and args.output_dir != args.raw_dir: 
    print(f"||    * {bcolors.BOLD}output dir{bcolors.ENDC}: [{args.output_dir}]")
else: 
    print(f"||{bcolors.WARNING}{bcolors.BOLD}    * output dir is the same as raw dir!{bcolors.ENDC}")

if args.fastq_dir:
    print(f"||    * {bcolors.BOLD}fastq dir{bcolors.ENDC}: [{args.fastq_dir}]")
if args.bed_dir: 
    print(f"||    * {bcolors.BOLD}bed dir{bcolors.ENDC}: [{args.bed_dir}]")
if args.peaks_dir: 
    print(f"||    * {bcolors.BOLD}peak dir{bcolors.ENDC}: [{args.peaks_dir}]")
if args.bam_dir: 
    print(f"||    * {bcolors.BOLD}bam dir{bcolors.ENDC}: [{args.bam_dir}]")
if args.bigwig_dir: 
    print(f"||    * {bcolors.BOLD}bw dir{bcolors.ENDC}: [{args.bigwig_dir}]")
if args.eq_dir: 
    print(f"||    * {bcolors.BOLD}quantification dir{bcolors.ENDC}: [{args.eq_dir}]")
print("||")
print(f"//========================================================================\\\\")

# ===========================================================================================================
STEP1 = "CHECKING STEPS AND ADDING DIRECTORIES IN DICTIONARY AND CREATING THEM"
# ===========================================================================================================

#### PROGRESS BAR #####
print(f"\n  {bcolors.BOLD}* Checking and creating directories for steps{bcolors.ENDC}\n")
with Progress() as progress:
    taskLength = len(task_list) -1
    task1 = progress.add_task("[red]Directories check", total=taskLength)

    while not progress.finished:

        #Create raw log directory
        if checkDir(configFileDict['raw_log']):
            vrb.bullet("Directory already exists. All log files will be written here.")
        else: 
            #vrb.bullet("Creating raw log directory.")
            createDir(configFileDict['raw_log'])


        if '1' in task_list:
            progress.update(task1, advance=1)
            if not args.fastq_dir:
                vrb.error("ERROR. you need to specify a fastq directory.")
            else:
                configFileDict['fastq_dir'] = args.fastq_dir 
            
            if args.output_dir:
                print("You specified an output directory.")
                configFileDict['trimmed_fastq_dir'] = f"{args.output_dir}/trimmed_fastq_dir"
            else: 
                configFileDict['trimmed_fastq_dir'] = f"{args.raw_dir}/trimmed_fastq"
            if checkDir(configFileDict['trimmed_fastq_dir']):
                vrb.error("Directory already exists. We refuse to write in already existing directories to avoid ovewriting or erasing files by mistake.")
            else: 
                createDir(configFileDict['trimmed_fastq_dir'])
                createLog(configFileDict['trimmed_fastq_dir'])
            print(f" * {bcolors.OKGREEN}Task 1 directory checks done{bcolors.ENDC}")
            time.sleep(0.1)
            
        if '1.1' in task_list: # QC of fastq files and multiQC to combine all of them
            progress.update(task1, advance=1)

            if not args.fastq_dir:
                vrb.error("ERROR. you need to specify a fastq directory.")
            else: 
                if '1' in task_list: 
                    print("Will run FastQC on raw and trimmed fastq files")
                else: 
                    configFileDict['fastq_dir'] = args.fastq_dir
            
            if args.output_dir:
                print("You specified an output directory.")
                configFileDict['fastQC_dir'] = f"{args.output_dir}/fastQC"
            else: 
                configFileDict['fastQC_dir'] = f"{args.raw_dir}/fastQC"
                #print(configFileDict['fastQC_dir'])
            if checkDir(configFileDict['fastQC_dir']): 
                vrb.error("Directory already exists. We refuse to write in already existing directories to avoid ovewriting or erasing files by mistake.")
            else: 
                createDir(configFileDict['fastQC_dir'])
                createLog(configFileDict['fastQC_dir'])
            print(f" * {bcolors.OKGREEN}Task 1.1 directory checks done{bcolors.ENDC}")
            time.sleep(0.1)


            
        if '2' in task_list:
            progress.update(task1, advance=1)

            if configFileDict['technology'] == "ATACseq" or configFileDict['technology'] == "ChIPseq": ## MAPs and sorts by coordinates
            # Arguments required here are -cf -raw -fastq -od
                if '1' not in task_list: 
                    if not args.fastq_dir: 
                        vrb.error("ERROR. You need to specify a fastq directory")
                    else:
                        configFileDict['trimmed_fastq_dir'] = args.fastq_dir 
                
                if args.output_dir:
                    print("You specified an output directory. The mapped bam files will be saved in the specified directory and the mapper will not automatically create a bam directory under the raw directory specified")
                    configFileDict['bam_dir'] = f"{args.output_dir}/bam"
                else: 
                    configFileDict['bam_dir'] = f"{args.raw_dir}/bam"
                if checkDir(configFileDict['bam_dir']): 
                    vrb.error("Directory already exists. We refuse to write in already existing directories to avoid ovewriting or erasing files by mistake.")
                else: 
                    createDir(configFileDict['bam_dir'])
                    createLog(configFileDict['bam_dir'])
            elif configFileDict['technology'] == "RNAseq":
                if '1' not in task_list: 
                    if not args.fastq_dir: 
                        vrb.error("ERROR. You need to specify a fastq directory")
                    else:
                        configFileDict['trimmed_fastq_dir'] = args.fastq_dir 

                if args.output_dir:
                    print("You specified an output directory. The mapped bam files will be saved in the specified directory and the mapper will not automatically create a bam directory under the raw directory specified")
                    configFileDict['bam_dir'] = f"{args.output_dir}/bam"
                else: 
                    configFileDict['bam_dir'] = f"{args.raw_dir}/bam"
                if checkDir(configFileDict['bam_dir']): 
                    vrb.error("Directory already exists. We refuse to write in already existing directories to avoid ovewriting or erasing files by mistake.")
                else: 
                    createDir(configFileDict['bam_dir'])
                    createLog(configFileDict['bam_dir'])
            
            else: 
                vrb.error("You need to specify a technology [ATACseq, ChIPseq, RNAseq] for the pipeline to work.")
            print(f" * {bcolors.OKGREEN}Task 2 directory checks done{bcolors.ENDC}")
            time.sleep(0.1)

        if '3' in task_list: ### PCR DUPLICATES MARK
            progress.update(task1, advance=1)
            if '2' not in task_list: 
                if not args.bam_dir: 
                    vrb.error("ERROR. You need to specify a bam directory")
                else:
                    configFileDict['bam_dir'] = args.bam_dir

            if args.output_dir: 
                print("You specified an output directory. The pipeline will therefore not create one.")
                configFileDict['marked_bam_dir'] = f"{args.output_dir}/marked_bam"
            else: 
                configFileDict['marked_bam_dir'] = f"{args.raw_dir}/marked_bam"
            if checkDir(configFileDict['marked_bam_dir']): 
                vrb.error("Directory already exists. We refuse to write in already existing directories to avoid ovewriting or erasing files by mistake.")
            else: 
                createDir(configFileDict['marked_bam_dir'])
                createLog(configFileDict['marked_bam_dir'])
            print(f" * {bcolors.OKGREEN}Task 3 directory checks done{bcolors.ENDC}")
            time.sleep(0.1)
            

        if '4' in task_list: ### FILTER/SORT/INDEX BAM FILES
            progress.update(task1, advance=1)
            if '3' not in task_list:
                if not args.bam_dir: 
                    vrb.error("ERROR. You need to specify a bam directory")
                else: 
                    configFileDict['marked_bam_dir'] = args.bam_dir 
            
            if args.output_dir: 
                print("You specified an output directory. The pipeline will therefore not create one.")
                configFileDict['filtered_bam_dir'] = f"{args.output_dir}/filtered_bam"
            else: 
                configFileDict['filtered_bam_dir'] = f"{args.raw_dir}/filtered_bam"
            if checkDir(configFileDict['filtered_bam_dir']): 
                vrb.error("Directory already exists. We refuse to write in already existing directories to avoid ovewriting or erasing files by mistake.")
            else: 
                createDir(configFileDict['filtered_bam_dir'])
                createLog(configFileDict['filtered_bam_dir'])    
            print(f" * {bcolors.OKGREEN}Task 4 directory checks done{bcolors.ENDC}")
            time.sleep(0.1)

        if '4.1' in task_list or '4.2' in task_list: # Create fragment Size distribution plots. 
            progress.update(task1, advance=1)
            if '4' not in task_list: 
                if not args.bam_dir: 
                    vrb.error("You need to specify a bam directory.")
                else: 
                    configFileDict['filtered_bam_dir'] = args.bam_dir 
            if args.output_dir: 
                print("You specified an output directory. The pipeline will therefore not create one.")
                configFileDict['bamQC_dir'] = f"{args.output_dir}/bamQC"
            else: 
                configFileDict['bamQC_dir'] = f"{args.raw_dir}/bamQC"
            if checkDir(configFileDict['bamQC_dir']): 
                vrb.error("Directory already exists. We refuse to write in already existing directories to avoid ovewriting or erasing files by mistake.")
            else: 
                createDir(configFileDict['bamQC_dir'])
                createLog(configFileDict['bamQC_dir']) 
            print(f" * {bcolors.OKGREEN}Task 4.1 directory checks done{bcolors.ENDC}")
            time.sleep(0.1)
            
        if '5' in task_list: ## CREATE BIGWIG
            progress.update(task1, advance=1)
            if '4' not in task_list: 
                if not args.bam_dir: 
                    vrb.error("You need to specify a bam directory.")
                else: 
                    configFileDict['filtered_bam_dir'] = args.bam_dir 
            
            if args.output_dir: 
                print("You specified an output directory. The pipeline will therefore not create one.")
                configFileDict['bw_dir'] = f"{args.output_dir}/bigwig"
            else: 
                configFileDict['bw_dir'] = f"{args.raw_dir}/bigwig"
            if checkDir(configFileDict['bw_dir']): 
                vrb.error("Directory already exists. We refuse to write in already existing directories to avoid ovewriting or erasing files by mistake.")
            else: 
                createDir(configFileDict['bw_dir'])
                createLog(configFileDict['bw_dir']) 
            print(f" * {bcolors.OKGREEN}Task 5 directory checks done{bcolors.ENDC}")
            time.sleep(0.1)
            
        if '6' in task_list: #### BAM 2 BED 
            progress.update(task1, advance=1)
            if '4' not in task_list: 
                if not args.bam_dir: 
                    vrb.error("You need to specify a bam directory.")
                else: 
                    configFileDict['filtered_bam_dir'] = args.bam_dir
            
            if args.output_dir: 
                print("You specified an output directory. The pipeline will therefore not create one.")
                configFileDict['bed_dir'] = f"{args.output_dir}/bed"
            else: 
                configFileDict['bed_dir'] = f"{args.raw_dir}/bed"
            if checkDir(configFileDict['bed_dir']): 
                vrb.error("Directory already exists. We refuse to write in already existing directories to avoid ovewriting or erasing files by mistake.")
            else: 
                createDir(configFileDict['bed_dir'])
                createLog(configFileDict['bed_dir']) 
            print(f" * {bcolors.OKGREEN}Task 6 directory checks done{bcolors.ENDC}")
            time.sleep(0.1)
                
        if '7' in task_list: 
            progress.update(task1, advance=1)
            if '6' not in task_list: 
                if not args.bed_dir: 
                    vrb.error("You need to specify a bed directory")
                else: 
                    configFileDict['bed_dir'] = args.bed_dir 
            
            if args.output_dir: 
                print("You specified an output directory. The pipeline will therefore not create one.")
                configFileDict['extended_bed_dir'] = f"{args.output_dir}/extended_bed"
            else: 
                configFileDict['extended_bed_dir'] = f"{args.raw_dir}/extended_bed"
            if checkDir(configFileDict['extended_bed_dir']): 
                vrb.error("Directory already exists. We refuse to write in already existing directories to avoid ovewriting or erasing files by mistake.")
            else: 
                createDir(configFileDict['extended_bed_dir'])
                createLog(configFileDict['extended_bed_dir'])
            print(f" * {bcolors.OKGREEN}Task 7 directory checks done{bcolors.ENDC}")
            time.sleep(0.1)
 
        if '8' in task_list:
            progress.update(task1, advance=1)
            if configFileDict['technology'] == "ATACseq" or configFileDict['technology'] == "ChIPseq": 
                if '7' not in task_list: 
                    if not args.bed_dir: 
                        vrb.error("You need to specify a bed directory")
                    else: 
                        configFileDict['extended_bed_dir'] = args.bed_dir
                if args.output_dir: 
                    print("You specified an output directory. The pipeline will therefore not create one.")
                    configFileDict['peaks_dir'] = f"{args.output_dir}/peaks"
                else: 
                    configFileDict['peaks_dir'] = f"{args.raw_dir}/peaks"
                if checkDir(configFileDict['peaks_dir']): 
                    vrb.error("Directory already exists. We refuse to write in already existing directories to avoid ovewriting or erasing files by mistake.")
                else: 
                    createDir(configFileDict['peaks_dir'])
                    createLog(configFileDict['peaks_dir'])
            else: 
                vrb.error("You need to specify a technology, either ATACseq, ChIPseq")
            print(f" * {bcolors.OKGREEN}Task 8 directory checks done{bcolors.ENDC}")
            time.sleep(0.1)
            
        if '8.1' in task_list:
            progress.update(task1, advance=1)
            if configFileDict['technology'] == "ATACseq" or configFileDict['technology'] == "ChIPseq": 
                if '8' not in task_list:
                    if not args.peaks_dir: 
                        vrb.error("You need to specify a bed directory")
                    else: 
                        configFileDict['peaks_dir'] = args.peaks_dir
                if '7' not in task_list: 
                    if not args.bed_dir: 
                        vrb.error("You need to specify a bed directory")
                    else: 
                        configFileDict['extended_bed_dir'] = args.bed_dir
                        
                if args.output_dir: 
                    print("You specified an output directory. The pipeline will therefore not create one.")
                    configFileDict['peakCounts_dir'] = f"{args.output_dir}/peakCounts"
                else: 
                    configFileDict['peakCounts_dir'] = f"{args.raw_dir}/peakCounts"
                if checkDir(configFileDict['peakCounts_dir']): 
                    vrb.error("Directory already exists. We refuse to write in already existing directories to avoid ovewriting or erasing files by mistake.")
                else: 
                    createDir(configFileDict['peakCounts_dir'])
                    createLog(configFileDict['peakCounts_dir'])
            else: 
                vrb.error("You need to specify a technology, either ATACseq, ChIPseq")
            print(f" * {bcolors.OKGREEN}Task 8.1 directory checks done{bcolors.ENDC}")
            time.sleep(0.1)


        if '9' in task_list: # EXON QUANTIFICATION 
            progress.update(task1, advance=1)
            if configFileDict['technology'] != "RNAseq": 
                vrb.warning("This step performs exon quantification but it appears you are not using RNAseq data. Please either change the technology to RNAseq or make sure you are using RNAseq data.")
            if '2' not in task_list: 
                if not args.bam_dir: 
                    vrb.error("You need to specify a bam directory")
                else: 
                    configFileDict['bam_dir'] = args.bam_dir
            if args.output_dir: 
                print("You specified an output directory. The pipeline will therefore not create one.")
                configFileDict['quantification_dir'] = f"{args.output_dir}/quantification"
            else: 
                configFileDict['quantification_dir'] = f"{args.raw_dir}/quantification"
            if checkDir(configFileDict['quantification_dir']): 
                print("fuck")
                vrb.error("Directory already exists. We refuse to write in already existing directories to avoid ovewriting or erasing files by mistake.")
            else: 
                createDir(configFileDict['quantification_dir'])
                createLog(configFileDict['quantification_dir'])
            print(f" * {bcolors.OKGREEN}Task 9 directory checks done{bcolors.ENDC}")
            time.sleep(0.1)


        if 'report' in task_list: 
            progress.update(task1, advance=1)
            if 'report' in task_list and len(task_list) == 1:
                vrb.error("The report step is used only in case you run all the steps.")
            if args.output_dir:
                configFileDict['report_dir'] = f"{args.output_dir}/report"
            else: 
                configFileDict['report_dir'] = f"{args.raw_dir}/report"
            if checkDir(configFileDict['report_dir']):
                vrb.error("ERROR. The report directory already exist. We refuse to write in already existing directories to avoid ovewriting or erasing files by mistake.")
            else:
                createDir(configFileDict['report_dir'])
                createLog(configFileDict['report_dir'])
            print(f" * {bcolors.OKGREEN}Report directory checks done{bcolors.ENDC}")
            time.sleep(0.1)



########################
##### START TASKS ###### 
########################

vrb.boldBullet("Starting\n")
print(bcolors.BOLD + "  * Unique ID of this run: " + bcolors.ENDC + bcolors.OKBLUE + str(configFileDict['uid']) + bcolors.ENDC + "\n")
#vrb.bullet(task_list)
task_dico = {} ### Dictionary containing for each task the wait_key so that I can automatically find out which is the last run task and get the wait_key instead of checking all of them one by one with if statements.
task_log_dico = {}

with Progress() as progress: 
    task1 = progress.add_task("[red]Submitting jobs", total=len(task_list))

    while not progress.finished:

        # ===========================================================================================================
        STEP1 = "Trimming reads"
        # ===========================================================================================================

        if '1' in task_list:
            vrb.boldBullet("Submitting trimming of reads.\n")   
            progress.update(task1, advance=1)
            
            fastq_dir = configFileDict['fastq_dir']
            FASTQ_FILES = getFastqPrefix(fastq_dir)
            #print(FASTQ_FILES)
            configFileDict['trim_log_files'] = [] 
            configFileDict['sample_prefix'] = FASTQ_FILES
            TRIM_WAIT = submitTrimming(configFileDict, FASTQ_FILES)
            configFileDict['TRIM_WAIT'] = TRIM_WAIT
            #submitJobCheck(configFileDict,'trim_log_files',TRIM_WAIT)
            task_dico['1'] = "TRIM_WAIT"
            
            task_log_dico['1'] = 'trim_log_files'

        # ===========================================================================================================
        STEP1_1 = "FASTQC"
        # ===========================================================================================================

        if '1.1' in task_list: 
            vrb.boldBullet("Submitting QC of fastq files\n")
            progress.update(task1, advance=1)
            configFileDict['fastqQC_log_files'] = []
            FASTQC_WAIT = submitFastQC(configFileDict)
            configFileDict['FASTQC_WAIT'] = FASTQC_WAIT
            #submitJobCheck(configFileDict, "fastqQC_log_files", FASTQC_WAIT)
            task_dico['1.1'] = "FASTQC_WAIT"
            
            vrb.boldBullet("Submitting multiqc to get all FastQC in a single report\n")
            configFileDict['multiqc_log_files'] = []
            FASTQC_WAIT = submitMultiQC(configFileDict)
            #submitJobCheck(configFileDict, "multiqc_log_files", MFASTQC_WAIT)    
            task_log_dico['1.1'] = 'fastqQC_log_files'
            

        #  ===========================================================================================================
        STEP2 = "Mapping reads / sorting bam files"
        # ===========================================================================================================
            
        if '2' in task_list: 
            vrb.boldBullet("Submitting mapping of reads.\n")
            progress.update(task1, advance=1)
            configFileDict['mapping_log_files'] = []
            if '1' not in task_list:
                FASTQ_PREFIX=getFastqPrefix(configFileDict['trimmed_fastq_dir'])
                FASTQ_PATH=configFileDict['trimmed_fastq_dir']
                configFileDict['sample_prefix'] = FASTQ_PREFIX # What if For trimming and mapping steps I created a list with all sample IDs in configFileDict so that I can just read it from there instead of creating variables all the time?? an just 
            else:
                FASTQ_PREFIX=getFastqPrefix(configFileDict['fastq_dir'])
                FASTQ_PATH=configFileDict['fastq_dir']
                configFileDict['sample_prefix'] = FASTQ_PREFIX
            
            if configFileDict["mapper"] == "bowtie2":
                MAP_WAIT = submitMappingBowtie(configFileDict, FASTQ_PREFIX, FASTQ_PATH)
            elif configFileDict['mapper'] == "STAR":
                MAP_WAIT = submitMappingSTAR(configFileDict, FASTQ_PREFIX)    
            else: 
                vrb.error("You need to specify a mapper")
            
            configFileDict['MAP_WAIT'] = MAP_WAIT                
            #submitJobCheck(configFileDict,'mapping_log_files',MAP_WAIT)
            task_dico['2'] = "MAP_WAIT"
            
            task_log_dico['2'] = 'mapping_log_files'

        # ===========================================================================================================
        STEP3 = "Marking duplicated reads"
        # ===========================================================================================================
                
        if '3' in task_list:
            vrb.boldBullet("Submitting PCR duplication detection using PICARD\n")
            progress.update(task1, advance=1)
            configFileDict['pcr_log_files'] = []
            if '1' in task_list or '2' in task_list:
                BAM_FILES = ["{}/{}.sortedByCoord.bam".format(configFileDict['bam_dir'],i) for i in configFileDict['sample_prefix']]
                
                PCR_DUPLICATION_WAIT = submitPCRduplication(configFileDict,BAM_FILES)
                configFileDict['PCR_DUPLICATION_WAIT'] = PCR_DUPLICATION_WAIT
            else:        
                BAM_FILES = glob.glob("{}/*.bam".format(configFileDict['bam_dir']))
                PCR_DUPLICATION_WAIT = submitPCRduplication(configFileDict,BAM_FILES)
                configFileDict['PCR_DUPLICATION_WAIT'] = PCR_DUPLICATION_WAIT
            #submitJobCheck(configFileDict,'pcr_log_files',PCR_DUPLICATION_WAIT)
            task_dico['3'] = "PCR_DUPLICATION_WAIT" 
            
            task_log_dico['3'] = 'pcr_log_files'

        # ===========================================================================================================
        STEP4 = "Filtering reads and indexing bam file"
        # ===========================================================================================================  

        if '4' in task_list: 
            vrb.bullet("Submitting filtering and sorting of BAM files\n")
            progress.update(task1, advance=1)
            configFileDict['filtering_log_files'] = []
            if '3' not in task_list:    
                BAM_FILES = glob.glob("{}/*.bam".format(configFileDict['marked_bam_dir']))
                FILTER_BAM_WAIT = submitFilteringBAM(configFileDict, BAM_FILES)
                configFileDict['FILTER_BAM_WAIT'] = FILTER_BAM_WAIT
            else:
                BAM_FILES = ["{}/{}.sortedByCoord.Picard.bam".format(configFileDict['marked_bam_dir'], i) for i in configFileDict['sample_prefix']]
                FILTER_BAM_WAIT = submitFilteringBAM(configFileDict, BAM_FILES)
                configFileDict['FILTER_BAM_WAIT'] = FILTER_BAM_WAIT
            #submitJobCheck(configFileDict,'filtering_log_files',FILTER_BAM_WAIT)
            task_dico['4'] = "FILTER_BAM_WAIT"
            
            task_log_dico['4'] = 'filtering_log_files'

        # ===========================================================================================================
        STEP4_1 = "FragmentSizeDist plot. QC STEP"
        # ===========================================================================================================

        if '4.1' in task_list:
            vrb.boldBullet("Submitting creation of ATACseq Fragment size distribution plots")
            progress.update(task1, advance=1)
            configFileDict['atacQC_log_files'] = []
            if '4' not in task_list:
                BAM_FILES = glob.glob("{}/*.bam".format(configFileDict['filtered_bam_dir']))
                ATACQC_WAIT = submitATACseqQC(configFileDict, BAM_FILES)
                configFileDict['ATACQC_WAIT'] = ATACQC_WAIT
            else: 
                BAM_FILES = ["{}/{}.QualTrim_NoDup_NochrM_SortedByCoord.bam".format(configFileDict['filtered_bam_dir'], i) for i in configFileDict['sample_prefix']]
                ATACQC_WAIT = submitATACseqQC(configFileDict, BAM_FILES)
                configFileDict['ATACQC_WAIT'] = ATACQC_WAIT
            task_dico['4.1'] = "ATACQC_WAIT"

            task_log_dico['4.1'] = 'atacQC_log_files'

        # ===========================================================================================================
        STEP4_2 = "QC STEP: bamQC"
        # ===========================================================================================================

        if '4.2' in task_list:
            vrb.boldBullet("Submitting bamQC stats generation")
            progress.update(task1, advance=1)
            configFileDict['bamQC_log_files'] = []
            
            if '4' not in task_list:
                BAM_FILES = glob.glob("{}/*.bam".format(configFileDict['filtered_bam_dir']))
                BAMQC_WAIT = submitBamQC(configFileDict, BAM_FILES)
                configFileDict['BAMQC_WAIT'] = BAMQC_WAIT
            else: 
                BAM_FILES = ["{}/{}.QualTrim_NoDup_NochrM_SortedByCoord.bam".format(configFileDict['filtered_bam_dir'], i) for i in configFileDict['sample_prefix']] + ["{}/{}.sortedByCoord.Picard.bam".format(configFileDict['marked_bam_dir'], i) for i in configFileDict['sample_prefix']] + ["{}/{}.sortedByCoord.bam".format(configFileDict['bam_dir'], i) for i in configFileDict['sample_prefix']]
                
                BAMQC_WAIT = submitBamQC(configFileDict, BAM_FILES)
                configFileDict['BAMQC_WAIT'] = BAMQC_WAIT
            
            task_dico['4.2'] = "BAMQC_WAIT"

            task_log_dico['4.2'] = 'bamQC_log_files'

        # ===========================================================================================================
        STEP5 = "BIG WIG files creation."
        # ===========================================================================================================   

        if '5' in task_list: 
            vrb.boldBullet("Submitting BAM to bigwig")
            progress.update(task1, advance=1)
            configFileDict['bw_log_files'] = []
            if '4' not in task_list:
                BAM_FILES = glob.glob("{}/*.bam".format(configFileDict['filtered_bam_dir']))
                BAM2BW_WAIT = submitBAM2BW(configFileDict, BAM_FILES)
                configFileDict['BAM2BW_WAIT'] = BAM2BW_WAIT
            else: 
                BAM_FILES = ["{}/{}.QualTrim_NoDup_NochrM_SortedByCoord.bam".format(configFileDict['filtered_bam_dir'], i) for i in configFileDict['sample_prefix']]
                BAM2BW_WAIT = submitBAM2BW(configFileDict, BAM_FILES)
                configFileDict['BAM2BW_WAIT'] = BAM2BW_WAIT
            #submitJobCheck(configFileDict,'bw_log_files',BAM2BW_WAIT)
            task_dico['5'] = "BAM2BW_WAIT"

            task_log_dico['5'] = 'bw_log_files'
            

        # ===========================================================================================================
        STEP6 = "BAM 2 BED"
        # ===========================================================================================================   

        if '6' in task_list: # Need to wait for '4' or none
            vrb.bullet("Submitting bam2bed")
            progress.update(task1, advance=1)
            configFileDict['bam2bed_log_files'] = []
            if '4' not in task_list:
                BAM_FILES = glob.glob("{}/*.bam".format(configFileDict['filtered_bam_dir']))
                BAM2BED_WAIT = submitBAM2BED(configFileDict, BAM_FILES)
                configFileDict['BAM2BED_WAIT'] = BAM2BED_WAIT
            else: 
                BAM_FILES = ["{}/{}.QualTrim_NoDup_NochrM_SortedByCoord.bam".format(configFileDict['filtered_bam_dir'], i) for i in configFileDict['sample_prefix']]
                BAM2BED_WAIT = submitBAM2BED(configFileDict, BAM_FILES)
                configFileDict['BAM2BED_WAIT'] = BAM2BED_WAIT
            #submitJobCheck(configFileDict,'bam2bed_log_files',BAM2BED_WAIT)
            task_dico['6'] = "BAM2BED_WAIT"
            
            task_log_dico['6'] = 'bam2bed_log_files'
            

        # ===========================================================================================================
        STEP7 = "Extend bed reads"
        # ===========================================================================================================   

        if '7' in task_list:
            vrb.bullet("Submitting extension of reads in bed file")
            progress.update(task1, advance=1)
            configFileDict['extend_log_files'] = []
            if '4' not in task_list:
                BED_FILES = glob.glob("{}/*.bed".format(configFileDict['bed_dir']))
                EXT_BED_WAIT = submitExtendReads(configFileDict, BED_FILES)
                configFileDict['EXT_BED_WAIT'] = EXT_BED_WAIT
            else: 
                BED_FILES = ["{}/{}.bed".format(configFileDict['bed_dir'], i) for i in configFileDict['sample_prefix']]
                EXT_BED_WAIT = submitExtendReads(configFileDict, BED_FILES)
                configFileDict['EXT_BED_WAIT'] = EXT_BED_WAIT
            #submitJobCheck(configFileDict,'extend_log_files',EXT_BED_WAIT)   
            
            task_dico["7"] = "EXT_BED_WAIT"
            task_log_dico['7'] = 'extend_log_files'

        # ===========================================================================================================
        STEP8 = "PEAK CALLING"
        # ===========================================================================================================

        if '8' in task_list: 
            vrb.boldBullet("Submitting peak calling\n")
            progress.update(task1, advance=1)
            configFileDict['peak_log_files'] = []
            if configFileDict['technology'] == "ATACseq":
                if '7' not in task_list: 
                    BED_FILES = glob.glob("{}/*.bed".format(configFileDict['extended_bed_dir']))
                    PEAK_CALLING_WAIT = submitPeakCalling(configFileDict, BED_FILES)
                    configFileDict['PEAK_CALLING_WAIT'] = PEAK_CALLING_WAIT
                else: 
                    BED_FILES = ["{}/{}.extendedReads.bed".format(configFileDict['extended_bed_dir'], i) for i in configFileDict['sample_prefix']]
                    PEAK_CALLING_WAIT = submitPeakCalling(configFileDict, BED_FILES)
                    configFileDict['PEAK_CALLING_WAIT'] = PEAK_CALLING_WAIT
            #submitJobCheck(configFileDict,'peak_log_files',PEAK_CALLING_WAIT)
            elif configFileDict['technology'] == "ChIPseq":
                if '7' not in task_list: 
                    FILES = glob.glob("{}/*.bed".format(configFileDict['extended_bed_dir']))
                    INPUTS= sorted([i for i in FILES if os.path.basename(i).split("_")[0] == "Input"])
                    SAMPLE_BED = sorted([i for i in FILES if os.path.basename(i).split("_")[0] != "Input"])
                    BED_FILES = [(i,j) for i,j in zip(SAMPLE_BED,INPUTS) if os.path.basename(i).split(".")[0] == os.path.basename(j).split(".")[0].split("_")[1]]
                    if len(BED_FILES) != len(SAMPLE_BED):
                        vrb.error("Samples and Inputs files do not match!")
                        
                    PEAK_CALLING_WAIT = submitChIPseqPeakCalling(configFileDict, BED_FILES)
                    configFileDict['PEAK_CALLING_WAIT'] = PEAK_CALLING_WAIT
                else: 
                    FILES = ["{}/{}.extendedReads.bed".format(configFileDict['extended_bed_dir'], i) for i in configFileDict['sample_prefix']]
                    #print(FILES)
                    INPUTS= sorted([i for i in FILES if os.path.basename(i).split("_")[0] == "Input"])
                    SAMPLE_BED = sorted([i for i in FILES if os.path.basename(i).split("_")[0] != "Input"])
                    BED_FILES = [(i,j) for i,j in zip(SAMPLE_BED,INPUTS) if os.path.basename(i).split(".")[0] == os.path.basename(j).split(".")[0].split("_")[1]]
                    #print(BED_FILES)
                    PEAK_CALLING_WAIT = submitChIPseqPeakCalling(configFileDict, BED_FILES)
                    configFileDict['PEAK_CALLING_WAIT'] = PEAK_CALLING_WAIT
            else:
                vrb.error("You are trying to run peak calling with data that is neither ATAC-seq nor ChIP-seq. Did you forget to change the technology?")
                
                
                
            task_dico["8"] = "PEAK_CALLING_WAIT"
            task_log_dico['8'] = 'peak_log_files'
            

        # ===========================================================================================================
        STEP8_1 = "PEAK2COUNTS"
        # ===========================================================================================================

        if '8.1' in task_list: 
            vrb.bullet("Submitting peak 2 Counts\n")
            progress.update(task1, advance=1)
            configFileDict['peak2Count_log_files'] = []
            if '8' not in task_list : 
                NARROWPEAK_FILES = glob.glob("{}/*.MACS/*.narrowPeak".format(configFileDict['peaks_dir']))
            else:
                if configFileDict['technology'] == "ATACseq": 
                    NARROWPEAK_FILES = ["{outputDir}/{samples}.MACS/{samples}_peaks.narrowPeak".format(outputDir = configFileDict['peaks_dir'], samples = i) for i in configFileDict['sample_prefix']]
                else: 
                    NARROWPEAK_FILES = ["{outputDir}/{samples}.MACS/{samples}_peaks.narrowPeak".format(outputDir = configFileDict['peaks_dir'], samples = i) for i in configFileDict['sample_prefix'] if i.split("_")[0] != "Input"]
            
            if '7' not in task_list:
                EXTENDED_BED_FILES = glob.glob("{}/*.bed".format(configFileDict['extended_bed_dir']))
            else:
                EXTENDED_BED_FILES = ["{}/{}.extendedReads.bed".format(configFileDict['extended_bed_dir'], i) for i in configFileDict['sample_prefix'] if os.path.basename(i).split("_")[0] != "Input"]
            
            PEAK2COUNT_CALLING_WAIT = submitPeak2Counts(configFileDict, NARROWPEAK_FILES,EXTENDED_BED_FILES)
            configFileDict['PEAK2COUNT_CALLING_WAIT'] = PEAK2COUNT_CALLING_WAIT
            #submitJobCheck(configFileDict,'peak2Count_log_files',PEAK2COUNT_CALLING_WAIT)
            
            task_dico["8.1"] = "PEAK2COUNT_CALLING_WAIT"
            task_log_dico['8.1'] = 'peak2Count_log_files'


        # ===========================================================================================================
        STEP9 = "EXON QUANTIFICATION - EXCLUSIVE FOR RNASEQ DATA"
        # ===========================================================================================================

        if '9' in task_list:
            vrb.boldBullet("Submitting exon/gene quantification\n")
            progress.update(task1, advance=1)
            configFileDict['quant_log_files'] = []
            if '2' not in task_list:
                BAM_FILES = glob.glob("{}/*.bam".format(configFileDict['bam_dir']))
                QUANT_WAIT = submitExonQuantification(configFileDict, BAM_FILES)
                configFileDict['QUANT_WAIT'] = QUANT_WAIT
                
        
            else:
                BAM_FILES = ["{}/{}.Aligned.sortedByCoord.out.bam".format(configFileDict['bam_dir'], i) for i in configFileDict['sample_prefix']]
                if configFileDict['quantificationSoftware'] == "QTLtools":
                    QUANT_WAIT = submitQTLtoolsExonQuantification(configFileDict, BAM_FILES)
                elif configFileDict['quantificationSoftware'] == "featureCounts":
                    QUANT_WAIT = submitFeatureCountsGeneQuantification(configFileDict, BAM_FILES)
                else: 
                    vrb.error("You need to specify which software to use for gene quantification")
            configFileDict['QUANT_WAIT'] = QUANT_WAIT    
            task_dico['9'] = 'QUANT_WAIT'
            task_log_dico['9'] = 'quant_log_files'

        # ===========================================================================================================
        STEP_JOBCHECK = "CHECKING SLURM OUTPUT FOR SUCCESSFUL EXIT CODES"
        # ===========================================================================================================

        wait_condition = []
        LOG_FILES = []
        for task in task_list: 
            if task == "report": 
                pass 
            else: 
                wait_condition.append(configFileDict[task_dico[task]])
                LOG_FILES.append(configFileDict[task_log_dico[task]])

        wait_condition = ",".join(wait_condition)
        logFiles = [item for sublist in LOG_FILES for item in sublist]
                
        JOBCHECK_WAIT = submitJobCheck2(configFileDict,logFiles, wait_condition)
        configFileDict['JOBCHECK_WAIT'] = JOBCHECK_WAIT    
        # ===========================================================================================================
        REPORT = "CREATING REPORT"
        # ===========================================================================================================
        # Need to add all summary statistics and png plots in report directory. 
        # Need to create unique file with all metrics and add it in the report. 
        # Need to gather all the exit codes from all steps to check status. 

        # Merge bamQC summary statistics csv files in report directory 
        # Copy png plots in report directory 
        # Gather for each step the exit codes and check whether everything was successful.
        # Write the report 
        # Save and export report

        if 'report' in task_list: 
            progress.update(task1, advance=1)
            #convert configFileDict and task_dico to file.
            outputDir = configFileDict['output_dir'] if args.output_dir else configFileDict['raw_dir']    
            reportDir = configFileDict['report_dir']
            
            dict2File(configFileDict,f"{reportDir}/configFileDict.json")
            dict2File(task_log_dico,f"{reportDir}/task_log_dico.json")
            
            configFileDict['report_log_file'] = []
            
            
            wait_condition = ",".join([configFileDict[task_dico[lst]] for lst in task_list if lst != "report"])
            jobcheck_wait = configFileDict['JOBCHECK_WAIT']
            wait_condition = wait_condition + "," + jobcheck_wait
            
            
            json1 = f"{reportDir}/configFileDict.json"
            json2 = f"{reportDir}/task_log_dico.json"
            
            if '1.1' in task_list: 
                cp_multiqc = "cp {fastqc}/multiqc_report.html {reportDir}/".format(fastqc = configFileDict['fastQC_dir'], reportDir = reportDir)
                
                zipDir_cmd = "python3 {zipScript} {reportDir} {raw_dir}/pipeline_report.zip".format(zipScript = configFileDict['zipDirectoryScript'], reportDir = reportDir, raw_dir = outputDir)
                
                CMD = "{python3} {report_script} {json1} {json2} {output_dir}/test_report.md; {cp_multiqc}; {zipDir_cmd}; rm {json1} {json2}".format(python3 = configFileDict['python'], report_script = configFileDict['report'], json1 = json1, json2 = json2,output_dir = reportDir, cp_multiqc = cp_multiqc, zipDir_cmd = zipDir_cmd)
            else:
                    
                zipDir_cmd = "python3 {zipScript} {reportDir} {raw_dir}/pipeline_report.zip".format(zipScript = configFileDict['zipDirectoryScript'], reportDir =reportDir, raw_dir = outputDir)
                
                CMD = "{python3} {report_script} {json1} {json2} {output_dir}/test_report.md; {zipDir_cmd}; rm {json1} {json2}".format(python3 = configFileDict['python'], report_script = configFileDict['report'], json1 = json1, json2 = json2,output_dir = reportDir, zipDir_cmd = zipDir_cmd)
            
            # Create .sh file to run the command. 
            
            SLURM = "{wsbatch} --dependency=afterok:{JID} -o {output_dir}/slurm-%j.out --wrap=\"{cmd}\"".format(wsbatch=configFileDict['wsbatch'], JID = wait_condition, cmd=CMD, output_dir = f"{reportDir}/log")
        
            
            out = subprocess.check_output(SLURM, shell=True, universal_newlines=True,stderr=subprocess.STDOUT)
            REPORT_WAIT = "".join(catchJID(out))
            configFileDict['REPORT_WAIT'] = REPORT_WAIT
            configFileDict['report_log_file'].append(getSlurmLog("{}/log".format(configFileDict["report_dir"]),configFileDict['uid'],out))
            task_dico['report'] = "REPORT_WAIT"
            task_log_dico['report'] = 'report_log_file'
    
    progress.stop()

########################
##### MAIL REPORT ######
########################

### Mail start of pipeline 
subject = "Pipeline started"
pipeline_start = datetime.now()
dt_string = pipeline_start.strftime("%d/%m/%Y %H:%M:%S")
steps = ",".join(configFileDict['task_list'])
addresses = [configFileDict['contact_email']]

if not args.output_dir:
    msg = "The pipeline started at {time}. All results will be written under {raw_dir}.\nThe steps that will be run are {steps}.".format(raw_dir = configFileDict['raw_dir'],time=dt_string, steps=steps, uid = configFileDict['uid'])
else:
    msg = "The pipeline started {time}. All results will be written under {raw_dir}.\nThe unique identifier of the pipeline run is: {uid}\nThe steps that will be run are {steps}.".format(raw_dir = configFileDict['output_dir'],steps=steps, uid=configFileDict['uid'],time=dt_string)

#writeEmail(addresses,subject,msg)

# Mail that pipeline ended # 
wait_condition = []
for t in task_list:
        wait_condition.append(configFileDict[task_dico[t]])


wait_condition = ",".join(wait_condition)
if not args.output_dir:
    msg = "The pipeline ended. All results can be found under {raw_dir}.\nThe steps that were ran were {steps}.".format(raw_dir = configFileDict['raw_dir'], steps=steps, uid = configFileDict['uid'])
    
else:
    msg = "The pipeline ended. All results can be found under {raw_dir}.\nThe steps that were ran were {steps}.".format(raw_dir = configFileDict['output_dir'], steps=steps, uid = configFileDict['uid'])
    

outputDir = configFileDict['output_dir'] if args.output_dir else configFileDict['raw_dir']    
DONE_CMD = "python3 {mail} -add {addresses} -subject {subject} -msg '{msg}' -join {outputDir}/pipeline_report.zip".format(mail=configFileDict['mail_script'], subject = "Pipeline_finished", msg= msg, addresses = " ".join(addresses),outputDir= outputDir)


SLURM_CMD = "{wsbatch} -o {raw_log}/{uid}_slurm-%j.out --dependency=afterok:{JID} --wrap=\"{cmd}\"".format(wsbatch = configFileDict['wsbatch'], raw_log = configFileDict['raw_log'], uid = configFileDict['uid'],JID = wait_condition, cmd = DONE_CMD)
out = subprocess.check_output(SLURM_CMD, shell=True, universal_newlines=True, stderr=subprocess.STDOUT)




