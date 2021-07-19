#!/usr/bin/env python3 

import subprocess
import sys 
import os 
import time 
from collections import defaultdict
import glob

pipeline_path = os.path.abspath(sys.path[0]).replace("pipeline_tools","")
pipeline_tools_path = os.path.abspath(pipeline_path + "/pipeline_tools")
utils_tools_path = os.path.abspath(pipeline_path+"/utils")
sys.path.append(pipeline_tools_path)
sys.path.append(utils_tools_path)
from verbose import verbose as vrb
from jobCheck import * 
from Logger import Log
from datetime import datetime

#1. Combine bamQC stats and copy to report directory
#2. Copy plots to report directory
#3. Get dictionary with all steps and exit codes. 
#4. Start report.


######## COMBINE bamQC and copy in report directory ##########

def combineBamQC(configFileDict, task_dico):
    wait_condition = ",".join([configFileDict[task_dico[lst]] for lst in configDict['task_list'] if lst != "report"])
    print(wait_condition)
    vrb.bullet("Merge all bamQC statistics into single csv file.")
    if configFileDict['technology'] == "ATACseq" or configFileDict['technology'] == "ChIPseq":
        input_dir = configFileDict['atacQC_dir']
        output_dir = configFileDict['report_dir']
        output_log = configFileDict['report_dir'] + "/log"
        sampleID = configFileDict['sample_prefix']
        samples_csvs = [input_dir + "/" + i +"_bamQC_stats.csv" for i in sampleID]
        
        merge_cmd = "awk 'NR==1 || FNR>1' {sample} > {input_dir}/Allsamples_bamQC_stats.csv && cp {input_dir}/Allsamples_bamQC_stats.csv {output_dir}/Allsamples_bamQC_stats.csv ".format(input_dir=input_dir, output_dir = output_dir,sample=",".join(samples_csvs))
        return merge_cmd 


def copyPlot(configFileDict, task_dico):
    vrb.bullet("Copy all plots to report directory")
    if configFileDict['technology'] == "ATACseq" or configFileDict['technology'] == "ChIPseq":
        input_dir = configFileDict['atacQC_dir']
        output_dir = configFileDict['report_dir']
        output_log = configFileDict['report_dir'] + "/log"
        sampleID = configFileDict['sample_prefix']
        samples_plots = [input_dir + "/" + i +"_fragSizeDistPlot.png" for i in sampleID]
        
        cp_plots = "cp {samples_plots} {output_dir}/".format(input_dir = input_dir, output_dir=output_dir,samples_plots=",".join(samples_plots))
    return cp_plots 

def getAllExitCodesPerTask(configFileDict,task_dico):
    
    vrb.bullet("Checking Exit Codes of task: "+task)
    dico = defaultdict(dict)
    for task in configFileDict['task_list']:
        logFiles = configFileDict[task_dico[task]]
        for file in logFiles:
            dico[task][file][check_exitCodes(file)]
    return dico 

            
def main(configFileDict, task_dico,reportName):
    TASKS = {'1':"Trimming", "1.1":"FastQC", "2":"Mapping",'3':"Marking Duplicates",'4':"Filtering&Indexing", '4.1':"QC of ATACseq", "4.2":"BamQC", "5":"Bam 2 BigWig", '6':"Bam 2 BED","7":"extending reads","8":"Peak Calling"}
    
    
    
    #1 combine bamQC data
    COMBINE_CMD = subprocess.Popen(combineBamQC(configFileDict,task_dico),shell=True, universal_newlines=True, stderr=subprocess.STDOUT)
    #2 copy plots to report directory 
    COPY_CMD = subprocess.Popen(copyPlot(configFileDict, task_dico),shell=True, universal_newlines=True, stderr=subprocess.STDOUT)
    
    #3 Get all exit Codes per task 
    
    dico = getAllExitCodesPerTask(configFileDict,task_dico)
    
    # Start creation of report
    date = datetime.now().strftime("%d/%m/%Y")

    log = Log(reportName) # Initialize logger
    log.ctitle("Testing pipeline report", "Nikolaos Lykoskoufis",date)
    
    for task in configFileDict['task_dico']:
        log.title(TASKS[task])
        logFiles = dico[task]
        code_set = set()
        FAILED = []
        for log,exitCode in logFiles.items():
            if not exitCode:
                FAILED.append(log)
            else:
                continue
        if len(FAILED)!=0:
            log.bold("Some jobs have failed.")
            for i in FAILED: 
                log.text(i)
        else:
            log.bold("All jobs have sucesssfully complteted for this step")
    
    log.heading1("ATAC seq QC plots")
    plots = glob.glob(configFileDict['report_dir']+"/*.png")
    if len(plots) == 0: 
        print("No plots to add to report")
    else: 
        for plot in plots:
            plot_title = plot.replace(".png","")
            log.image(plot_title, plot)         
    
            
    # wrapping up and converting markdown to html 
    log.md2html(reportName.replace(".md", ".html"))    


if __name__ == "__main__":
    main(*sys.argv[1:])
    
    

