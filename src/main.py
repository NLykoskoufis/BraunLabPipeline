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
from slurmTools import *
from dirCheck import * 
from submitSteps import *

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'




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
2. MAP reads to reference genome & SORT ==> Wait for 1 is 1 is needed to run
3. Mark PCR duplicates ==> WAIT FOR 2
4. REMOVE PCR duplicates, vendor QUAL control and secondary alignment and INDEX ==> WAIT FOR 3
4.1 Create Fragment Size Distribution plots
5. CREATE .bw for visualization <INDEPENDENT STEP FROM 8,9,10> => ONLY NEED TO WAIT FOR 6 TO BE DONE. 
6. CONVERT bam2bed ==> Wait for 6 to be done
7. Bed file with extended reads ==> Wait for 8
8. PEAK Calling ==> Wait for 9
#===============================================================================
"""


parser = argparse.ArgumentParser(description='Pipeline to process data from illumina sequencers.')
parser.add_argument('-v', dest='version', action='store_true', help='Display pipeline version')
#If user is asking for version
if len(sys.argv) > 1:
    if sys.argv[1] == '-v':
        print('Pipeline version 1.00\n')
        sys.exit(0)

parser.add_argument('-raw', '--raw-dir', dest='raw_dir',required=True, type=str, help='Absolute path to the raw directory')
parser.add_argument('-fastq', '--fast-qdir', dest='fastq_dir', type=str, help='Absolut path fastq to diretor(y)ies. If multiple directories, separate eache path with space')
#parser.add_argument('-trimfastq', '--trim-fastq-dir', dest='trimmed_fastq_dir', type=str, help='Absolut path trimmed fastq to diretor(y)ies. If multiple directories, separate eache path with space')
parser.add_argument('-bam', '--bam-dir', dest='bam_dir', type=str, help='Path bam diretory, is multiple, separate with space.')
#parser.add_argument('-sortedBam','--sorted-bam-dir', dest='sorted_bam_dir', type=str, help='Path to sorted bam directory, if not set, first bam directory is used.')
parser.add_argument('-eqd','--quant-dir', '-quantification_dir', dest='eq_dir', type=str, help='Absolut path peak calling diretory')
parser.add_argument('-bed', '--bed-dir', dest='bed_dir', type=str, help='Absolut path of where to save/read bed files')
parser.add_argument('-bw', '--bigwig-dir', dest='bigwig_dir', type=str, help='Absolut path peak calling diretory')
parser.add_argument('-od', '--output-dir', dest='output_dir', type=str, help='Path to output directory. Use it only if you do not run the pipeline from step')
parser.add_argument('-cf','--configuration-file', dest='config_file_path', required=True,type=str, help='Name of your configuration file: project_run_config_V1')
#parser.add_argument('-tf', dest='tar_fastq', action='store_true', help='True if you want to do a backup of fastq files. \'-rn\' and \'-pn\' options are mandatory to do a backup.')
#parser.add_argument('-tb', dest='tar_bam', action='store_true', help='True if you want to do a backup of bam files. \'-rn\' and \'-pn\' options are mandatory to do a backup.')
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

#get list of tasks

if not args.task:
    sys.stderr.write('ERROR: You must give task(s) to run : arg -t\n')
    sys.exit(1)
task_list = args.task
if configFileDict['technology'] == "ATACseq":
    if 'all' in task_list:
        task_list = ['1','2','3','4','4.1','5','6','7','8']
elif configFileDict['technology'] == "ChIPSeq":
    if 'all' in task_list: 
        task_list = ['1','2','3','4','4.1','5','6','7','8'] # TO BE CONFIRMED
elif configFileDict['technology'] == "RNAseq":
    if 'all' in task_list: 
        task_list = ['2','4','9']
    if '3' or '4' in task_list: 
        print("WARNING!!! It is not recommended to remove duplicated reads for RNAseq experiments as you may kill your signal for very highly expressed genes.")
    if '8' in task_list:
        sys.stderr("ERROR. You cannot call peaks from RNAseq data.")
    if '5' in task_list or '6' in task_list or '7' in task_list:
        print("WARNING! These are not RNAseq data specific steps.")
else: 
    sys.stderr("ERROR. The pipeline can only process ATACseq, ChIPseq or RNAseq data. PLease specify one of them in the configuration file")

task_list.append("last")
    


if not args.raw_dir: 
    raise TypeError("ERROR. You need to specify a raw directory for the pipeline to work")
else: 
    configFileDict['raw_dir'] = args.raw_dir

if args.raw_dir and not args.output_dir: 
    print("The raw directory is also the output directory")
if args.raw_dir and args.output_dir: 
    print("Results will be written in the output directory specified and not the raw directory")

if args.raw_dir == args.output_dir:
    raise TypeError("ERROR. The raw directory and output directories are the same. Either specify a different output directory than the raw directory or do not specify at all.")

#Create unique ID for the run
configFileDict["uid"] = (str(uuid.uuid1())[:8])

# Add extra information to the dictionary
configFileDict["pipeline_path"] = pipeline_path

### WHICH STEPS ARE GOING TO BE RAN AND CHECK WHETHER ALL DIRECTORIES WERE GIVEN 
configFileDict['task_list'] = task_list 

# ===========================================================================================================
STEP1 = "CHECKING STEPS AND ADDING DIRECTORIES IN DICTIONARY AND CREATING THEM"
# ===========================================================================================================

if '1' in task_list: 
    if not args.fastq_dir:
        raise TypeError("ERROR. you need to specify a fastq directory.")
    else: 
        configFileDict['fastq_dir'] = args.fastq_dir 
    
    if args.output_dir:
        print("You specified an output directory.")
        configFileDict['trimmed_fastq_dir'] = f"{args.output_dir}/trimmed_fastq_dir"
    else: 
        configFileDict['trimmed_fastq_dir'] = f"{args.raw_dir}/trimmed_fastq"
    if checkDir(configFileDict['trimmed_fastq_dir']): 
        raise FileExistsError("Directory already exists. We refuse to write in already existing directories to avoid ovewriting or erasing files by mistake.")
    else: 
        createDir(configFileDict['trimmed_fastq_dir'])
        createLog(configFileDict['trimmed_fastq_dir'])
    
    
    
if '2' in task_list: ## MAPs and sorts by coordinates
    # Arguments required here are -cf -raw -fastq -od
    if '1' not in task_list: 
        if not args.fastq_dir: 
            raise TypeError("ERROR. You need to specify a fastq directory")
        else:
            configFileDict['trimmed_fastq_dir'] = args.fastq_dir 
    
    if args.output_dir:
        print("You specified an output directory. The mapped bam files will be saved in the specified directory and the mapper will not automatically create a bam directory under the raw directory specified")
        configFileDict['bam_dir'] = f"{args.output_dir}/bam"
        configFileDict['sorted_bam_dir'] = f"{args.output_dir}/sorted_bam"
    else: 
        configFileDict['bam_dir'] = f"{args.raw_dir}/bam"
        configFileDict['sorted_bam_dir'] = f"{args.raw_dir}/sorted_bam"
    if checkDir(configFileDict['bam_dir']) and checkDir(configFileDict['sorted_bam_dir']): 
        raise FileExistsError("Directory already exists. We refuse to write in already existing directories to avoid ovewriting or erasing files by mistake.")
    else: 
        createDir(configFileDict['bam_dir'])
        createLog(configFileDict['bam_dir'])
        createDir(configFileDict['sorted_bam_dir'])
        createLog(configFileDict['sorted_bam_dir'])
        
        

if '3' in task_list: ### PCR DUPLICATES MARK
    if '2' not in task_list: 
        if not args.bam_dir: 
            raise TypeError("ERROR. You need to specify a bam directory")
        else:
            configFileDict['sorted_bam_dir'] = args.bam_dir

    if args.output_dir: 
        print("You specified an output directory. The pipeline will therefore not create one.")
        configFileDict['marked_bam_dir'] = f"{args.output_dir}/marked_bam"
    else: 
        configFileDict['marked_bam_dir'] = f"{args.raw_dir}/marked_bam"
    if checkDir(configFileDict['marked_bam_dir']): 
        raise FileExistsError("Directory already exists. We refuse to write in already existing directories to avoid ovewriting or erasing files by mistake.")
    else: 
        createDir(configFileDict['marked_bam_dir'])
        createLog(configFileDict['marked_bam_dir'])
    
    

if '4' in task_list: ### FILTER/SORT/INDEX BAM FILES
    if '3' not in task_list:
        if not args.bam_dir: 
            raise TypeError("ERROR. You need to specify a bam directory")
        else: 
            configFileDict['marked_bam_dir'] = args.bam_dir 
    
    if args.output_dir: 
        print("You specified an output directory. The pipeline will therefore not create one.")
        configFileDict['filtered_bam_dir'] = f"{args.output_dir}/filtered_bam"
    else: 
        configFileDict['filtered_bam_dir'] = f"{args.raw_dir}/filtered_bam"
    if checkDir(configFileDict['filtered_bam_dir']): 
        raise FileExistsError("Directory already exists. We refuse to write in already existing directories to avoid ovewriting or erasing files by mistake.")
    else: 
        createDir(configFileDict['filtered_bam_dir'])
        createLog(configFileDict['filtered_bam_dir'])    


if '4.1' in task_list: # Create fragment Size distribution plots. 
    if '4' not in task_list: 
        if not args.bam_dir: 
            raise TypeError("You need to specify a bam directory.")
        else: 
            configFileDict['filtered_bam_dir'] = args.bam_dir 
    if args.output_dir: 
        print("You specified an output directory. The pipeline will therefore not create one.")
        configFileDict['atacQC_dir'] = f"{args.output_dir}/ATACseqQC"
    else: 
        configFileDict['atacQC_dir'] = f"{args.raw_dir}/ATACseqQC"
    if checkDir(configFileDict['atacQC_dir']): 
        raise FileExistsError("Directory already exists. We refuse to write in already existing directories to avoid ovewriting or erasing files by mistake.")
    else: 
        createDir(configFileDict['atacQC_dir'])
        createLog(configFileDict['atacQC_dir']) 

if '5' in task_list: ## CREATE BIGWIG
    if '4' not in task_list: 
        if not args.bam_dir: 
            raise TypeError("You need to specify a bam directory.")
        else: 
            configFileDict['filtered_bam_dir'] = args.bam_dir 
    
    if args.output_dir: 
        print("You specified an output directory. The pipeline will therefore not create one.")
        configFileDict['bw_dir'] = f"{args.output_dir}/bigwig"
    else: 
        configFileDict['bw_dir'] = f"{args.raw_dir}/bigwig"
    if checkDir(configFileDict['bw_dir']): 
        raise FileExistsError("Directory already exists. We refuse to write in already existing directories to avoid ovewriting or erasing files by mistake.")
    else: 
        createDir(configFileDict['bw_dir'])
        createLog(configFileDict['bw_dir']) 
        
if '6' in task_list: #### BAM 2 BED 
    if '4' not in task_list: 
        if not args.bam_dir: 
             raise TypeError("You need to specify a bam directory.")
        else: 
            configFileDict['filtered_bam_dir'] = args.bam_dir
    
    if args.output_dir: 
        print("You specified an output directory. The pipeline will therefore not create one.")
        configFileDict['bed_dir'] = f"{args.output_dir}/bed"
    else: 
        configFileDict['bed_dir'] = f"{args.raw_dir}/bed"
    if checkDir(configFileDict['bed_dir']): 
        raise FileExistsError("Directory already exists. We refuse to write in already existing directories to avoid ovewriting or erasing files by mistake.")
    else: 
        createDir(configFileDict['bed_dir'])
        createLog(configFileDict['bed_dir']) 
    
        
if '7' in task_list: 
    if '6' not in task_list: 
        if not args.bed_dir: 
            raise TypeError("You need to specify a bed directory")
        else: 
            configFileDict['bed_dir'] = args.bed_dir 
    
    if args.output_dir: 
        print("You specified an output directory. The pipeline will therefore not create one.")
        configFileDict['extended_bed_dir'] = f"{args.output_dir}/extended_bed"
    else: 
        configFileDict['extended_bed_dir'] = f"{args.raw_dir}/extended_bed"
    if checkDir(configFileDict['extended_bed_dir']): 
        raise FileExistsError("Directory already exists. We refuse to write in already existing directories to avoid ovewriting or erasing files by mistake.")
    else: 
        createDir(configFileDict['extended_bed_dir'])
        createLog(configFileDict['extended_bed_dir'])


if '8' in task_list:
    if configFileDict['technology'] == "ATACseq": 
        if '7' not in task_list: 
            if not args.bed_dir: 
                raise TypeError("You need to specify a bed directory")
            else: 
                configFileDict['extended_bed_dir'] = args.bed_dir
        if args.output_dir: 
            print("You specified an output directory. The pipeline will therefore not create one.")
            configFileDict['peaks_dir'] = f"{args.output_dir}/peaks"
        else: 
            configFileDict['peaks_dir'] = f"{args.raw_dir}/peaks"
        if checkDir(configFileDict['peaks_dir']): 
            raise FileExistsError("Directory already exists. We refuse to write in already existing directories to avoid ovewriting or erasing files by mistake.")
        else: 
            createDir(configFileDict['peaks_dir'])
            createLog(configFileDict['peaks_dir'])


########################
##### START TASKS ###### 
########################

print(" * Starting\n")
print(f" * Unique ID of this run: {str(configFileDict['uid'])}\n")
print(task_list)


# ===========================================================================================================
STEP1 = "Trimming reads"
# ===========================================================================================================

if '1' in task_list: 
    print("Running trimming of reads.\n")
        
    fastq_dir = configFileDict['fastq_dir']
    FASTQ_FILES = getFastqPrefix(fastq_dir)
    print(FASTQ_FILES[0])
    configFileDict['trim_log_files'] = [] 
    configFileDict['sample_prefix'] = FASTQ_FILES
    TRIM_WAIT = submitTrimming(configFileDict, FASTQ_FILES)
    configFileDict['TRIM_WAIT'] = TRIM_WAIT
    submitJobCheck(configFileDict,'trim_log_files',TRIM_WAIT)
    
# ===========================================================================================================
STEP2 = "Mapping reads / sorting bam files"
# ===========================================================================================================
                
if '2' in task_list: 
    print("Running mapping of reads.\n")
    configFileDict['mapping_log_files'] = []
    if '1' not in task_list:
        FASTQ_PREFIX=getFastqPrefix(configFileDict['trimmed_fastq_dir'])
        FASTQ_PATH=configFileDict['trimmed_fastq_dir']
        configFileDict['sample_prefix'] = FASTQ_PREFIX
    else:
        FASTQ_PREFIX=getFastqPrefix(configFileDict['fastq_dir'])
        FASTQ_PATH=configFileDict['fastq_dir']
    if configFileDict["mapper"] == "bowtie2":
        MAP_WAIT = submitMappingBowtie(configFileDict, FASTQ_PREFIX, FASTQ_PATH)
        configFileDict['MAP_WAIT'] = MAP_WAIT                
    submitJobCheck(configFileDict,'mapping_log_files',MAP_WAIT)
    
# ===========================================================================================================
STEP3 = "Marking duplicated reads"
# ===========================================================================================================
        
if '3' in task_list:
    print(" * Running PCR duplication detection using PICARD\n")
    configFileDict['pcr_log_files'] = []
    if '1' in task_list or '2' in task_list:
        BAM_FILES = ["{}/{}.sortedByCoord.bam".format(configFileDict['sorted_bam_dir'],i) for i in configFileDict['sample_prefix']]
        print(BAM_FILES)
        PCR_DUPLICATION_WAIT = submitPCRduplication(configFileDict,BAM_FILES)
        configFileDict['PCR_DUPLICATION_WAIT'] = PCR_DUPLICATION_WAIT
    else:        
        BAM_FILES = glob.glob("{}/*.bam".format(configFileDict['sorted_bam_dir']))
        PCR_DUPLICATION_WAIT = submitPCRduplication(configFileDict,BAM_FILES)
        configFileDict['PCR_DUPLICATION_WAIT'] = PCR_DUPLICATION_WAIT
    submitJobCheck(configFileDict,'pcr_log_files',PCR_DUPLICATION_WAIT)

# ===========================================================================================================
STEP4 = "Filtering reads and indexing bam file"
# ===========================================================================================================  

if '4' in task_list: 
    print(" * Running filtering and sorting of BAM files\n")
    configFileDict['filtering_log_files'] = []
    if '3' not in task_list:    
        BAM_FILES = glob.glob("{}/*.bam".format(configFileDict['marked_bam_dir']))
        FILTER_BAM_WAIT = submitFilteringBAM(configFileDict, BAM_FILES)
        configFileDict['FILTER_BAM_WAIT'] = FILTER_BAM_WAIT
    else:
        BAM_FILES = ["{}/{}.sortedByCoord.Picard.bam".format(configFileDict['marked_bam_dir'], i) for i in configFileDict['sample_prefix']]
        FILTER_BAM_WAIT = submitFilteringBAM(configFileDict, BAM_FILES)
        configFileDict['FILTER_BAM_WAIT'] = FILTER_BAM_WAIT
    submitJobCheck(configFileDict,'filtering_log_files',FILTER_BAM_WAIT)


# ===========================================================================================================
STEP4_1 = "FragmentSizeDist plot. QC STEP"
# ===========================================================================================================

if '4.1' in task_list:
    print(" * Generating ATACseq Fragment size distribution plots")
    configFileDict['atacQC_log_files'] = []
    if '4' not in task_list:
        BAM_FILES = glob.glob("{}/*.bam".format(configFileDict['filtered_bam_dir']))
        ATACQC_WAIT = submitATACseqQC(configFileDict, BAM_FILES)
        configFileDict['ATACQC_WAIT'] = ATACQC_WAIT
    else: 
        BAM_FILES = ["{}/{}.QualTrim_NoDup_NochrM_SortedByCoord.bam".format(configFileDict['filtered_bam_dir'], i) for i in configFileDict['sample_prefix']]
        ATACQC_WAIT = submitATACseqQC(configFileDict, BAM_FILES)
        configFileDict['ATACQC_WAIT'] = ATACQC_WAIT
    submitJobCheck(configFileDict,'atacQC_log_files',ATACQC_WAIT)
 


# ===========================================================================================================
STEP5 = "BIG WIG files creation."
# ===========================================================================================================   

if '5' in task_list: 
    print(" * Generating bigwig files for visualization")
    configFileDict['bw_log_files'] = []
    if '4' not in task_list:
        BAM_FILES = glob.glob("{}/*.bam".format(configFileDict['filtered_bam_dir']))
        BAM2BW_WAIT = submitBAM2BW(configFileDict, BAM_FILES)
        configFileDict['BAM2BW_WAIT'] = BAM2BW_WAIT
    else: 
        BAM_FILES = ["{}/{}.QualTrim_NoDup_NochrM_SortedByCoord.bam".format(configFileDict['filtered_bam_dir'], i) for i in configFileDict['sample_prefix']]
        BAM2BW_WAIT = submitBAM2BW(configFileDict, BAM_FILES)
        configFileDict['BAM2BW_WAIT'] = BAM2BW_WAIT
    submitJobCheck(configFileDict,'bw_log_files',BAM2BW_WAIT)
    

# ===========================================================================================================
STEP6 = "BAM 2 BED"
# ===========================================================================================================   

if '6' in task_list: # Need to wait for '4' or none
    print (" * Running bam2bed")
    configFileDict['bam2bed_log_files'] = []
    if '4' not in task_list:
        BAM_FILES = glob.glob("{}/*.bam".format(configFileDict['filtered_bam_dir']))
        BAM2BED_WAIT = submitBAM2BED(configFileDict, BAM_FILES)
        configFileDict['BAM2BW_WAIT'] = BAM2BED_WAIT
    else: 
        BAM_FILES = ["{}/{}.QualTrim_NoDup_NochrM_SortedByCoord.bam".format(configFileDict['filtered_bam_dir'], i) for i in configFileDict['sample_prefix']]
        BAM2BED_WAIT = submitBAM2BED(configFileDict, BAM_FILES)
        configFileDict['BAM2BED_WAIT'] = BAM2BED_WAIT
    submitJobCheck(configFileDict,'bam2bed_log_files',BAM2BED_WAIT)

# ===========================================================================================================
STEP7 = "Extend bed reads"
# ===========================================================================================================   

if '7' in task_list:
    print(" * Running extension of reads in bed file")
    configFileDict['extend_log_files'] = []
    if '4' not in task_list:
        BED_FILES = glob.glob("{}/*.bed".format(configFileDict['bed_dir']))
        EXT_BED_WAIT = submitExtendReads(configFileDict, BED_FILES)
        configFileDict['EXT_BED_WAIT'] = EXT_BED_WAIT
    else: 
        BED_FILES = ["{}/{}.bed".format(configFileDict['bed_dir'], i) for i in configFileDict['sample_prefix']]
        EXT_BED_WAIT = submitExtendReads(configFileDict, BED_FILES)
        configFileDict['EXT_BED_WAIT'] = EXT_BED_WAIT
    submitJobCheck(configFileDict,'extend_log_files',EXT_BED_WAIT)   
# ===========================================================================================================
STEP8 = "PEAK CALLING"
# ===========================================================================================================

if '8' in task_list: 
    print(" * Running peak calling\n")
    configFileDict['peak_log_files'] = []
    if '6' not in task_list: 
        BED_FILES = glob.glob("{}/*.bed".format(configFileDict['extended_bed_dir']))
        PEAK_CALLING_WAIT = submitPeakCalling(configFileDict, BED_FILES)
        configFileDict['PEAK_CALLING_WAIT'] = PEAK_CALLING_WAIT
    else: 
        BED_FILES = ["{}/{}.extendedReads.bed".format(configFileDict['extended_bed_dir'], i) for i in configFileDict['sample_prefix']]
        PEAK_CALLING_WAIT = submitPeakCalling(configFileDict, BED_FILES)
        configFileDict['PEAK_CALLING_WAIT'] = PEAK_CALLING_WAIT
    submitJobCheck(configFileDict,'peak_log_files',PEAK_CALLING_WAIT)





