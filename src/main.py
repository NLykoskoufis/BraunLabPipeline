#!/usr/bin/env python3 

import subprocess
import sys 
import os 
import time 
import argparse
from collections import defaultdict
import uuid

pipeline_path = sys.path[0]
pipeline_tools_path = os.path.abspath(pipeline_path + "/pipeline_tools")

sys.path.append(pipeline_tools_path)
from writeEmail import writeEmail
from configParser import getConfigDict


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

parser.add_argument('-fastq', '-fastqdir', dest='fastq_dir', type=str, nargs='+', help='Absolut path fastq to diretor(y)ies. If multiple directories, separate eache path with space')
parser.add_argument('-bam', '-bamdir', dest='bam_dir', type=str, nargs='+', help='Path bam diretory, is multiple, separate with space.')
parser.add_argument('-sortedBam', dest='sorted_bam_dir', type=str, nargs=1, help='Path to sorted bam directory, if not set, first bam directory is used.')
parser.add_argument('-eqd', '-quantification_dir', dest='eq_dir', type=str, nargs='+', help='Absolut path peak calling diretory')
parser.add_argument('-od', '-outputdir', dest='output_dir', type=str, nargs=1, help='Path to output directory')
parser.add_argument('-cf', dest='config_file_path', type=str, nargs=1, help='Name of your configuration file: project_run_config_V1')
parser.add_argument('-tf', dest='tar_fastq', action='store_true', help='True if you want to do a backup of fastq files. \'-rn\' and \'-pn\' options are mandatory to do a backup.')
parser.add_argument('-tb', dest='tar_bam', action='store_true', help='True if you want to do a backup of bam files. \'-rn\' and \'-pn\' options are mandatory to do a backup.')
parser.add_argument('-t', dest='task', type=str, required=True, nargs='+', help='')
parser.add_argument("-email", dest="email_address", type=list, required=False, nargs='+', help="Mail address(es) to send updates about pipeline run")

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
    if not args.config_file_list_path:
        sys.stderr.write('ERROR: You must provide a configuration file to run the pipeline : arg -cf\n')
        sys.exit(1)
    elif not os.path.exists(args.config_file_path):
        sys.stderr.write('ERROR: The configuration file you provided does not exist')
        sys.exit(1)
    else: 
        configFileDict = getConfigDict(args.configFilepath) # Create dictionay containing all important information for the pipeline to work. 
        
   
    


