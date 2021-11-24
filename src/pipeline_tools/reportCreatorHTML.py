#!/usr/bin/env python3 

import json

from reportCreator import HtmlReport
from ColorBamQC import *
from collections import defaultdict 
import os 
import sys
import datetime

def readDictFromFile(dico):
    f = open(dico)
    
    dict = json.load(f)
    return dict

def getAllExitCodesPerTask(configFileDict,task_dico):
    dico = defaultdict(dict)
    for task in configFileDict['task_list']:
        #vrb.bullet(task)
        if task == "report":
            continue
        else:
            #vrb.bullet("Checking Exit Codes of task: "+task)
            #print(task_dico[task])
            logFiles = configFileDict[task_dico[task]]
            #print(logFiles)
            for file in logFiles:
 
                dico[task][file] = check_exitCodes(file)
    return dico


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

def createLogListForReport(dico,task):
    lst = []
    logFiles = dico[task]
    for l, exitCode in logFiles.items():
        if exitCode: 
            lst.append(f"{l}: <span style=\"color:green\">Successfully completed</span>")
        else: 
            lst.append(f"{l}: <span style=\"color:red\">Failed</span>")    
    return lst
        

def copyPlot(configFileDict, task_dico):
    #vrb.bullet("Copy all plots to report directory")
    if configFileDict['technology'] == "ATACseq" or configFileDict['technology'] == "ChIPseq":
        input_dir = configFileDict['bamQC_dir']
        output_dir = configFileDict['report_dir']
        output_log = configFileDict['report_dir'] + "/log"
        sampleID = configFileDict['sample_prefix']
        samples_plots = [input_dir + "/" + i +"_fragSizeDistPlot.pdf" for i in sampleID]
    elif configFileDict['technology'] == "RNAseq":
        print("TBD")
        
    cp_plots = "cp {samples_plots} {output_dir}/".format(input_dir = input_dir, output_dir=output_dir,samples_plots=" ".join(samples_plots))
    return cp_plots 

def getImageList(path, configFileDict):
    sampleID = configFileDict['sample_prefix']
    samplesPlots = [(path + "/" + i + "_fragSizeDistPlot.pdf",i) for i in sampleID]
    return samplesPlots
    
def ChIPseqGD():
    return "<section>\n  <table border=\"1\" class=\"dfStandards\" id=\"dfS\">\n    <thead>\n    <tr style=\"text-align: center;\">\n        <th colspan=\"6\">ChIPseq library complexity standards</th>\n      </tr>\n      <tr style=\"text-align: center;\">\n        <th>PBC1</th>\n        <th>PBC2</th>\n        <th>Bottlenecking level</th>\n        <th>NRF</th>\n        <th>Complexity</th>\n        <th>Flag colors</th>\n      </tr>\n    </thead>\n    <tbody>\n      <tr>\n        <td> &lt; 0.5</td>\n        <td> &lt; 1</td>\n        <td>Severe</td>\n        <td> &lt; 0.5</td>\n        <td>Concerning</td>\n        <td style=\"background-color:orange; font-weight:bold\">Orange</td>\n      </tr>\n      <tr>\n        <td>0.5&GreaterEqual; PBC1 &lt; 0.8</td>\n        <td>1&GreaterEqual; PBC1 &lt; 3</td>\n        <td>Moderate</td>\n        <td>0.5&GreaterEqual; NRF &lt; 0.8</td>\n        <td>Acceptable</td>\n        <td style=\"background-color:yellow; font-weight:bold\">Yellow</td>\n      </tr>\n      <tr>\n        <td>0.8&GreaterEqual; PBC1 &lt; 0.9</td>\n        <td>3&GreaterEqual; PBC1 &lt; 10</td>\n        <td>Mild</td>\n        <td>0.8&GreaterEqual; NRF &lt; 0.9</td>\n        <td>Compliant</td>\n        <td style=\"background-color:#4dbd4d; font-weight:bold\">Green</td>\n      </tr>\n      <tr>\n        <td>&gt; 0.9</td>\n        <td>&gt; 10</td>\n        <td>None</td>\n        <td>&gt; 0.9</td>\n        <td>Ideal</td>\n        <td style=\"background-color:#4dbd4d; font-weight:bold\">Green</td>\n      </tr>\n    </tbody>\n  </table>\n</section>"  

def ATACseqGD():
    return "<section>\n  <table border=\"1\" class=\"dfStandards\" id=\"dfS\">\n    <thead>\n      <tr style=\"text-align: center;\">\n        <th colspan=\"6\">ATACseq library complexity standards</th>\n      </tr>\n      <tr>\n        <th>PBC1</th>\n        <th>PBC2</th>\n        <th>Bottlenecking level</th>\n        <th>NRF</th>\n        <th>Complexity</th>\n        <th>Flag colors</th>\n      </tr>\n    </thead>\n    <tbody>\n      <tr>\n        <td> &lt; 0.7</td>\n        <td> &lt; 1</td>\n        <td>Severe</td>\n        <td> &lt; 0.7</td>\n        <td>Concerning</td>\n        <td style=\"background-color:orange; font-weight:bold\">Orange</td>\n      </tr>\n      <tr>\n        <td>0.7&GreaterEqual; PBC1 &lt; 0.9</td>\n        <td>1&GreaterEqual; PBC2 &lt; 3</td>\n        <td>Moderate</td>\n        <td>0.7&GreaterEqual; NRF &GreaterEqual; 0.9</td>\n        <td>Acceptable</td>\n        <td style=\"background-color:yellow; font-weight:bold\">Yellow</td>\n      </tr>\n      <tr>\n        <td>&gt; 0.9</td>\n        <td>&gt; 3</td>\n        <td>None</td>\n        <td> &lt; 0.9</td>\n        <td>Ideal</td>\n        <td style=\"background-color:#4dbd4d; font-weight:bold\">Green</td>\n      </tr>\n    </tbody>\n  </table>\n</section>"



def main(configurationDictionary, task_dictionary, outputHTMLfile):
    configFileDict = readDictFromFile(configurationDictionary)    
    task_dico = readDictFromFile(task_dictionary)
    
    logDico = getAllExitCodesPerTask(configFileDict, task_dico)

    print(configFileDict['task_list'])

    print("  * Initiating html document")
    now = datetime.datetime.now()
    
    html = "" 
    x = HtmlReport(outputHTMLfile)
    html += x.initiate()
    os.system(f"cp {configFileDict['pipeline_path']}/report/ReportCreator.png {configFileDict['report_dir']}")
    html += x.header(f"{now.strftime('%Y-%m-%d %H:%M')}", configFileDict['raw_dir'])


    if '1' in configFileDict['task_list']:
        
        html += x.SectionCreator().initiateSection()
        html +=  x.h1("Trimming of reads (Task 1)")
        html += x.text("Results for the trimming can be accessed here:")
        html += x.addPathWithBackground(f"{configFileDict['raw_dir']}/trimmed_fastq")
        
        html += x.h3("Log Files")
        
        lst = x.listCreator()
        tasklogFiles = createLogListForReport(logDico, "1")
        html += lst.initiateList("logList") + "\n"
        for i in tasklogFiles: 
            html += lst.addElement(i) + "\n"
        html += lst.terminate()
        html += x.SectionCreator.terminateSection()

    if '1.1' in configFileDict['task_list']:
        
        html += x.SectionCreator().initiateSection()
        html += x.h1("Quality control of fastQC (Task 1.1)")
        html += x.text("The fastQC results can be found here")
        html += x.link("multiqc report",f"{configFileDict['report_dir']}/multiqc_report.html")
        html += x.SectionCreator().terminateSection()

    if '2' in configFileDict['task_list']:
        html += x.SectionCreator().initiateSection()
        html += x.h1("Mapping reads (Task 2)")

        html += x.text("Results for the mapping can be accessed here:")
        html += x.addPathWithBackground(f"{configFileDict['raw_dir']}/bam")
        
        html += x.h3("Log Files")
        tasklogFiles = createLogListForReport(logDico, "2")
        html += lst.initiateList("logList") + "\n"
        for i in tasklogFiles: 
            html += lst.addElement(i) + "\n"
        html += lst.terminate()
        html += x.SectionCreator.terminateSection()

    if '3' in configFileDict['task_list']:
        html += x.SectionCreator().initiateSection()
        html += x.h1("Marking duplicated reads (Task 3)")

        html += x.text("Results for the marking of duplicated reads can be accessed here:")
        html += x.addPathWithBackground(f"{configFileDict['raw_dir']}/marked_bam")
        
        html += x.h3("Log Files")
        tasklogFiles = createLogListForReport(logDico, "3")
        html += lst.initiateList("logList") + "\n"
        for i in tasklogFiles: 
            html += lst.addElement(i) + "\n"
        html += lst.terminate()
        html += x.SectionCreator.terminateSection()

    if '4' in configFileDict['task_list']:
        html += x.SectionCreator().initiateSection()
        html += x.h1("Filtering reads (Task 4)")

        html += x.text("Results for the filtering of reads reads can be accessed here:")
        html += x.addPathWithBackground(f"{configFileDict['raw_dir']}/filtered_bam")
        
        html += x.h3("Log Files")
        tasklogFiles = createLogListForReport(logDico, "4")
        html += lst.initiateList("logList") + "\n"
        for i in tasklogFiles: 
            html += lst.addElement(i) + "\n"
        html += lst.terminate()
        html += x.SectionCreator.terminateSection()

    if '5' in configFileDict['task_list']:
        html += x.SectionCreator().initiateSection()
        html += x.h1("BAM 2 BW (Task 5)")

        html += x.text("The bigwig files can be found here:")
        html += x.addPathWithBackground(f"{configFileDict['raw_dir']}/bigwig")
        
        html += x.h3("Log Files")
        tasklogFiles = createLogListForReport(logDico, "5")
        html += lst.initiateList("logList") + "\n"
        for i in tasklogFiles: 
            html += lst.addElement(i) + "\n"
        html += lst.terminate()
        html += x.SectionCreator.terminateSection()


    if '6' in configFileDict['task_list']:
        html += x.SectionCreator().initiateSection()
        html += x.h1("BAM 2 BED (Task 6)")

        html += x.text("The bed files can be found here:")
        html += x.addPathWithBackground(f"{configFileDict['raw_dir']}/bed")
        
        html += x.h3("Log Files")
        tasklogFiles = createLogListForReport(logDico, "6")
        html += lst.initiateList("logList") + "\n"
        for i in tasklogFiles: 
            html += lst.addElement(i) + "\n"
        html += lst.terminate()
        html += x.SectionCreator.terminateSection()

    if '7' in configFileDict['task_list']:
        html += x.SectionCreator().initiateSection()
        html += x.h1("Extend reads (Task 7)")

        html += x.text("The extended bed files can be found here:")
        html += x.addPathWithBackground(f"{configFileDict['raw_dir']}/extended_bed")
        
        html += x.h3("Log Files")
        tasklogFiles = createLogListForReport(logDico, "7")
        html += lst.initiateList("logList") + "\n"
        for i in tasklogFiles: 
            html += lst.addElement(i) + "\n"
        html += lst.terminate()
        html += x.SectionCreator.terminateSection()

    if '8' in configFileDict['task_list']:
        html += x.SectionCreator().initiateSection()
        html += x.h1("Peak quantification (Task 8)")

        html += x.text("The peak quantifications can be found here:")
        html += x.addPathWithBackground(f"{configFileDict['raw_dir']}/peaks")
        
        html += x.h3("Log Files")
        tasklogFiles = createLogListForReport(logDico, "8")
        html += lst.initiateList("logList") + "\n"
        for i in tasklogFiles: 
            html += lst.addElement(i) + "\n"
        html += lst.terminate()
        html += x.SectionCreator.terminateSection()

    if '8.1' in configFileDict['task_list']:
        html += x.SectionCreator().initiateSection()
        html += x.h1("Peak 2 counts (Task 8.1)")

        html += x.text("The peak counts can be found here:")
        html += x.addPathWithBackground(f"{configFileDict['raw_dir']}/peakCounts")
        
        html += x.h3("Log Files")
        tasklogFiles = createLogListForReport(logDico, "8.1")
        html += lst.initiateList("logList") + "\n"
        for i in tasklogFiles: 
            html += lst.addElement(i) + "\n"
        html += lst.terminate()
        html += x.SectionCreator.terminateSection()

    if '9' in configFileDict['task_list']:
        html += x.SectionCreator().initiateSection()
        html += x.h1("Gene quantifications (Task 9)")

        html += x.text("The gene quantifications can be found here:")
        html += x.addPathWithBackground(f"{configFileDict['raw_dir']}/quantifications")
        
        html += x.h3("Log Files")
        tasklogFiles = createLogListForReport(logDico, "9")
        html += lst.initiateList("logList") + "\n"
        for i in tasklogFiles: 
            html += lst.addElement(i) + "\n"
        html += lst.terminate()
        html += x.SectionCreator.terminateSection()

    if '4.1' in configFileDict['task_list'] or '4.2' in configFileDict['task_list']: 
        html += x.SectionCreator().initiateSection()
        html += x.h1("Quality control of BAM files")
        if '4.2' in configFileDict['task_list']:
            html += x.h2("Samtools BAM statistics")
            html += x.csv2html(f"{configFileDict['bamQC_dir']}/AllSamples_samtoolsStats.csv",table_id="bamQC", text_align="center")
            if configFileDict['technology'] == "ATACseq" or configFileDict['technology'] == "ChIPseq":
                if configFileDict['technology'] == "ATACseq":
                    html += x.h2("ATACseq bam QC")
                    html += x.text("THe table below represents the gold standards for ATACseq/ChIPseq data. More information can be found here.")
                    html += x.SectionCreator().initiateSection()
                    html += ATACseqGD()
                    html += x.SectionCreator().terminateSection()
                else:
                    html += x.h2("ChIPseq bam QC")
                    html += x.text("THe table below represents the gold standards for ATACseq/ChIPseq data. More information can be found here.")
                    html += x.SectionCreator().initiateSection()
                    html += ChIPseqGD()
                    html += x.SectionCreator().terminateSection()
                
                    
                html += x.SectionCreator().initiateSection()
                html += csvtoHTML(f"{configFileDict['bamQC_dir']}/Allsamples_bamQC_stats.csv")
                html += x.SectionCreator().terminateSection()
        html += x.SectionCreator().terminateSection()

    if '4.1' in configFileDict['task_list']:
        #imgList = getImageList("/Users/mnt/small_projects/learnHTML/figures",configFileDict)
        
        html += x.SectionCreator().initiateSection()
        html += x.h2("Fragment Size distribution")
        html += "<center>\n"
        html += x.addImage(f"{configFileDict['report_dir']}merged.pdf","Fragment Size distribution")
        html += "</center>\n"
        html += x.SectionCreator().terminateSection()

    html += x.footer()
    html += x.endReport()

    x.writeToFile(html)


if __name__ == "__main__":
    main(*sys.argv[1:])