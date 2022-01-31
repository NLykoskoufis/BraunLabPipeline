#!/usr/bin/env python3 

from distutils.command.config import config
import subprocess
import sys 
import glob
import os
from pipeline_tools.slurmTools import catchJID
from scripts.featureCountsTObed import combineCounts

pipeline_path = sys.path[0]
pipeline_tools_path = os.path.abspath(pipeline_path + "/pipeline_tools")
sys.path.append(pipeline_tools_path)
from slurmTools import *

def submitTrimming(configFileDict, FASTQ_PREFIX, dryRun=False):
    """Function that submits slurm jobs for trimming reads.

    Args:
        configFileDict ([dict]): [configuration file dictionary]
        FASTQ_PREFIX ([lst]): [List containing the FASTQ sample IDs]

    Returns:
        [str]: comma separated string containing slurm job IDs for wait condition
    """    
    TRIM_JID_LIST = []
    for file in FASTQ_PREFIX:

        if configFileDict['pairend'] == "1":
            TRIM_CMD = "{bin} {parameters} -o {trimmed_dir}/{file}.trim_S1_L001_R1_001.fastq.gz -p {trimmed_dir}/{file}.trim_S1_L001_R2_001.fastq.gz {fastq_dir}/{file}*_R1_001.fastq.gz {fastq_dir}/{file}*_R2_001.fastq.gz".format(bin=configFileDict["cutadapt"], parameters=configFileDict["trim_reads"], file=file, trimmed_dir = configFileDict["trimmed_fastq_dir"], fastq_dir=configFileDict['fastq_dir'])
        else:
            if configFileDict['RNAkit'] == "Colibri":
                BIN = configFileDict['cutadapt']
                INPUT = "{fastq_dir}/{file}*_R1_001.fastq.gz".format(fastq_dir = configFileDict['fastq_dir'], file = file)
                OUTPUT = "{trimmed_dir}/{file}.trim_S1_L001_R1_001.fastq.gz".format(trimmed_dir = configFileDict["trimmed_fastq_dir"], file = file)
                trimReadsCommand = configFileDict['trim_reads']
                trimReadsCommand = trimReadsCommand.replace("BIN",configFileDict['cutadapt']).replace("INPUT",INPUT).replace("OUTPUT",OUTPUT)
                TRIM_CMD = trimReadsCommand
    
            else:
                TRIM_CMD = "{bin} {parameters} -o {trimmed_dir}/{file}.trim_S1_L001_R1_001.fastq.gz  {fastq_dir}/{file}*_R1_001.fastq.gz ".format(bin=configFileDict["cutadapt"], parameters=configFileDict["trim_reads"], file=file, trimmed_dir = configFileDict["trimmed_fastq_dir"], fastq_dir=configFileDict['fastq_dir'])
            
        SLURM_CMD = "{wsbatch} {slurm} -o {trimmed_log_dir}/{uid}_slurm-%j.out --wrap=\"{cmd}\"".format(wsbatch = configFileDict["wsbatch"], slurm = configFileDict["slurm_trim"], trimmed_log_dir = "{}/log".format(configFileDict["trimmed_fastq_dir"]), uid = configFileDict["uid"], cmd = TRIM_CMD)
        
        if dryRun:
            print(SLURM_CMD)
            print()
        else:
            out = subprocess.check_output(SLURM_CMD, shell=True, universal_newlines= True, stderr=subprocess.STDOUT)
            TRIM_JID_LIST.append(catchJID(out))
        
            configFileDict['trim_log_files'].append(getSlurmLog("{}/log".format(configFileDict["trimmed_fastq_dir"]),configFileDict['uid'],out))
        
    if dryRun:
        return "dryRun"
    else:    
        TRIM_WAIT = ",".join(TRIM_JID_LIST)
        return TRIM_WAIT


def submitMappingBowtie(configFileDict, FASTQ_PREFIX, FASTQ_PATH, dryRun=False):
    """[Submits jobs for Mapping using Bowtie2]

    Args:
        configFileDict ([dict]): [configuration file dictionary]
        FASTQ_FILES ([lst]): [List containing the FASTQ sample IDs]
        FASTQ_PATH [str]: Absolute path of the FASTQ files
    Returns:
        [str]: [Returns the slurm Job IDs so that the jobs of the next step can wait until mapping has finished]
    """  
    MAP_JID_LIST = []
    configFileDict['mapping_log_files'] = []
    for file in FASTQ_PREFIX:                                                        

        
        if configFileDict['pairend'] ==  "1": 
            MAP_CMD = "{mapper} {parameters} -x {REFSEQ} -1 {dir}/{file}*_R1_001.fastq.gz -2 {dir}/{file}*_R2_001.fastq.gz | {samtools} view -b -h -o {bam_dir}/{file}.raw.bam && {samtools} sort -O BAM -o {bam_dir}/{file}.sortedByCoord.bam {bam_dir}/{file}.raw.bam && rm {bam_dir}/{file}.raw.bam && {samtools} index {bam_dir}/{file}.sortedByCoord.bam".format(mapper=configFileDict['bowtie2'], parameters=configFileDict['bowtie_parameters'],dir=FASTQ_PATH,file=file, samtools = configFileDict["samtools"], bam_dir=configFileDict['bam_dir'], REFSEQ=configFileDict['reference_genome'])
        else:
            MAP_CMD = "{mapper} {parameters} -x {REFSEQ} -U {dir}/{file}*_R1_001.fastq.gz | {samtools} view -b -h -o {bam_dir}/{file}.raw.bam && {samtools} sort -O BAM -o {bam_dir}/{file}.sortedByCoord.bam {bam_dir}/{file}.raw.bam && rm {bam_dir}/{file}.raw.bam && {samtools} index {bam_dir}/{file}.sortedByCoord.bam".format(mapper=configFileDict['bowtie2'], parameters=configFileDict['bowtie_parameters'],dir=FASTQ_PATH,file=file, samtools = configFileDict["samtools"], bam_dir=configFileDict['bam_dir'], REFSEQ=configFileDict['reference_genome']) 
        
        if '1' in configFileDict['task_list']: 
            SLURM_CMD = "{wsbatch} {slurm} -o {log_dir}/{uid}_slurm-%j.out --dependency=afterany:{JID} --wrap=\"{cmd}\"".format(wsbatch = configFileDict["wsbatch"], slurm = configFileDict["slurm_mapping"], log_dir = "{}/log".format(configFileDict['bam_dir']), uid = configFileDict["uid"], cmd = MAP_CMD, JID=configFileDict["TRIM_WAIT"])
            #print(SLURM_CMD)
        else: 
            SLURM_CMD = "{wsbatch} {slurm} -o {log_dir}/{uid}_slurm-%j.out --wrap=\"{cmd}\"".format(wsbatch = configFileDict["wsbatch"], slurm = configFileDict["slurm_mapping"], log_dir = f"{configFileDict['bam_dir']}/log", uid = configFileDict["uid"], cmd = MAP_CMD)
            #print(SLURM_CMD)
        
        if dryRun:
            print(SLURM_CMD)
        else:
            out = subprocess.check_output(SLURM_CMD, shell=True, universal_newlines= True, stderr=subprocess.STDOUT)
            MAP_JID_LIST.append(catchJID(out))
            configFileDict['mapping_log_files'].append(getSlurmLog("{}/log".format(configFileDict["bam_dir"]),configFileDict['uid'],out))
    
    if dryRun:
        return "dryRun"
    else:
        MAP_WAIT = ",".join(MAP_JID_LIST)
        #del MAP_JID_LIST
        return MAP_WAIT


def submitMappingSTAR(configFileDict, FASTQ_PREFIX, dryRun=False):
    """[Submits jobs for Mapping using STAR]

    Args:
        configFileDict ([dict]): [configuration file dictionary]
        FASTQ_FILES ([lst]): [List containing the FASTQ sample IDs]
        FASTQ_PATH [str]: Absolute path of the FASTQ files
    Returns:
        [str]: [Returns the slurm Job IDs so that the jobs of the next step can wait until mapping has finished]
    """  
    MAP_JID_LIST = []
    configFileDict['mapping_log_files'] = []
    
    pairend = configFileDict['pairend']
    STAR = configFileDict['star']
    ref_genome = configFileDict['reference_genome']
    annotation = configFileDict['annotation']
    readLength = configFileDict['STARreadLength']
    bamDir = configFileDict['bam_dir']
    fastqDir = configFileDict['trimmed_fastq_dir']
    logDir = bamDir + '/log/'

    sjdbOverhang = int(readLength)-int(1)
    
    for sample in FASTQ_PREFIX:                                                        


        if pairend == "0" :
            if configFileDict['RNAkit'] == "Colibri":
                STAR_CMD = "{STAR} {parameters} --outFileNamePrefix {outFileNamePrefix} --genomeDir {STARgenomeDir} --readFilesIn {fastq_dir}/{smp}*_R1_001.fastq.gz; {samtools} sort {outFileNamePrefix}Aligned.out.sam -O BAM -o {outFileNamePrefix}Aligned.sortedByCoord.out.bam; {samtools} index {outFileNamePrefix}Aligned.sortedByCoord.out.bam".format(STAR = STAR, outFileNamePrefix = f"{bamDir}/{sample}.", STARgenomeDir = configFileDict['reference_genome'], annotation = annotation, sjdbOverhand = str(sjdbOverhang), smp = sample, parameters = configFileDict['STARoptions'], fastq_dir = fastqDir, samtools = configFileDict['samtools'])
            else:    
                STAR_CMD = "{STAR} {parameters} --outFileNamePrefix {outFileNamePrefix} --genomeDir {STARgenomeDir} --readFilesIn {fastq_dir}/{smp}*_R1_001.fastq.gz --sjdbGTFfile {annotation} --sjdbOverhang {sjdbOverhand}; {samtools} index {outFileNamePrefix}Aligned.sortedByCoord.out.bam".format(STAR = STAR, outFileNamePrefix = f"{bamDir}/{sample}.", STARgenomeDir = configFileDict['reference_genome'], annotation = annotation, sjdbOverhand = str(sjdbOverhang), smp = sample, parameters = configFileDict['STARoptions'], fastq_dir = fastqDir, samtools = configFileDict['samtools'])
        else:
            STAR_CMD = "{STAR} {parameters} --outFileNamePrefix {outFileNamePrefix} --genomeDir {STARgenomeDir} --readFilesIn {fastq_dir}/{smp}*_R1_001.fastq.gz {fastq_dir}/{smp}*_R2_001.fastq.gz --sjdbGTFfile {annotation} --sjdbOverhang {sjdbOverhand}; {samtools} index {outFileNamePrefix}Aligned.sortedByCoord.out.bam".format(STAR = STAR, outFileNamePrefix = f"{bamDir}/{sample}.", STARgenomeDir = configFileDict['reference_genome'], annotation = annotation, sjdbOverhand = str(sjdbOverhang), smp = sample, parameters = configFileDict['STARoptions'], fastq_dir = fastqDir, samtools = configFileDict['samtools'])
   
        
        if '1' in configFileDict['task_list']: 
            SLURM_CMD = "{wsbatch} {slurm} -o {log_dir}/{uid}_slurm-%j.out --dependency=afterany:{JID} --wrap=\"{cmd}\"".format(wsbatch = configFileDict["wsbatch"], slurm = configFileDict["slurm_mapping"], log_dir = "{}/log".format(configFileDict['bam_dir']), uid = configFileDict["uid"], cmd = STAR_CMD, JID=configFileDict["TRIM_WAIT"])
            #print(SLURM_CMD)
        else: 
            SLURM_CMD = "{wsbatch} {slurm} -o {log_dir}/{uid}_slurm-%j.out --wrap=\"{cmd}\"".format(wsbatch = configFileDict["wsbatch"], slurm = configFileDict["slurm_mapping"], log_dir = f"{configFileDict['bam_dir']}/log", uid = configFileDict["uid"], cmd = STAR_CMD)
            #print(SLURM_CMD)
        
        if dryRun:
            print(SLURM_CMD)
        else:
            out = subprocess.check_output(SLURM_CMD, shell=True, universal_newlines= True, stderr=subprocess.STDOUT)
            MAP_JID_LIST.append(catchJID(out))
            configFileDict['mapping_log_files'].append(getSlurmLog("{}/log".format(configFileDict["bam_dir"]),configFileDict['uid'],out))
    
    if dryRun:
        return "dryRun"
    else:
        MAP_WAIT = ",".join(MAP_JID_LIST)
        return MAP_WAIT



def submitPCRduplication(configFileDict,BAM_FILES, dryRun=False):
    """[Submits jobs for marking PCR duplicated reads using PICARD]

    Args:
        configFileDict ([dict]): [configuration file dictionary]
        BAM_PATH ([lst]): [List containing the BAM file absolute path]

    Returns:
        [str]: [Returns the slurm Job IDs so that the jobs of the next step can wait until mapping has finished]
    """
    PCR_DUP_JID_LIST = []
          
    OUTPUT_DIR = configFileDict['marked_bam_dir']    
    for bam in BAM_FILES: 
        input = os.path.basename(bam).split(".")[0]
        OUTPUT_FILE = "{}/{}.sortedByCoord.Picard.bam".format(OUTPUT_DIR,input)
        
        METRIX_FILE = "{}/{}.metrix".format(OUTPUT_DIR,input)
        
        PCR_CMD = "{PICARD} MarkDuplicates I={input} O={output} M={metrix}; {samtools} index {output}".format(PICARD=configFileDict['picard'], input=bam, output=OUTPUT_FILE, metrix=METRIX_FILE, samtools = configFileDict['samtools'])
        
        if '2' in configFileDict['task_list']:
            SLURM_CMD = "{wsbatch} {slurm} -o {log_dir}/{uid}_slurm-%j.out --dependency=afterany:{JID} --wrap=\"{cmd}\"".format(wsbatch = configFileDict["wsbatch"], slurm = configFileDict["slurm_general"], log_dir = "{}/log".format(OUTPUT_DIR), uid = configFileDict["uid"], cmd = PCR_CMD, JID=configFileDict['MAP_WAIT'])
            #print(SLURM_CMD)
        else: 
            SLURM_CMD = "{wsbatch} {slurm} -o {log_dir}/{uid}_slurm-%j.out --wrap=\"{cmd}\"".format(wsbatch = configFileDict["wsbatch"], slurm = configFileDict["slurm_general"], log_dir = "{}/log".format(OUTPUT_DIR), uid = configFileDict["uid"], cmd = PCR_CMD)
        
        if dryRun:
            print(SLURM_CMD)
        else:
            out = subprocess.check_output(SLURM_CMD, shell=True, universal_newlines=True, stderr=subprocess.STDOUT)
            PCR_DUPLICATION_WAIT = PCR_DUP_JID_LIST.append(catchJID(out))
            configFileDict['pcr_log_files'].append(getSlurmLog("{}/log".format(configFileDict["marked_bam_dir"]),configFileDict['uid'],out))
    
    if dryRun:
        return "dryRun"
    else:
        PCR_DUPLICATION_WAIT = ",".join(PCR_DUP_JID_LIST)
        del PCR_DUP_JID_LIST 
        return PCR_DUPLICATION_WAIT

def submitFilteringBAM(configFileDict, BAM_FILES, dryRun=False):
    """[Submits jobs for filtering and sorting BAM files]

    Args:
        configFileDict ([dict]): [configuration file dictionary]
        BAM_FILES ([lst]): [List containing the BAM files]

    Returns:
        [str]: [Returns the slurm Job IDs so that the jobs of the next step can wait until mapping has finished]
    """
    BAM_FILTER_JID_LIST = []
    OUTPUT_DIR = configFileDict['filtered_bam_dir']
    for bam in BAM_FILES:
        input_file = os.path.basename(bam).split(".")[0]
        OUTPUT_FILE = "{}/{}.QualTrim_NoDup_NochrM_SortedByCoord.bam".format(OUTPUT_DIR, input_file)
        
        FILTER_CMD = "{samtools} view {arguments} -@ 4 {input} | grep -v 'chrM' | {samtools} view -b -o {output_file} -@ 4 && {samtools} index {output_file} -@ 4".format(samtools = configFileDict['samtools'], arguments=configFileDict['PCR_duplicates_removal'], input = bam, output_file = OUTPUT_FILE)
        
        
        if '3' in configFileDict['task_list']: 
            SLURM_CMD = "{wsbatch} {slurm} -o {log_dir}/{uid}_slurm-%j.out --dependency=afterany:{JID} --wrap=\"{cmd}\"".format(wsbatch = configFileDict["wsbatch"], slurm = configFileDict["slurm_filter_bam"], log_dir = "{}/log".format(OUTPUT_DIR), uid = configFileDict["uid"], cmd = FILTER_CMD, JID=configFileDict['PCR_DUPLICATION_WAIT'])
            #print(SLURM_CMD)
        else: 
            SLURM_CMD = "{wsbatch} {slurm} -o {log_dir}/{uid}_slurm-%j.out --wrap=\"{cmd}\"".format(wsbatch = configFileDict["wsbatch"], slurm = configFileDict["slurm_filter_bam"], log_dir = "{}/log".format(OUTPUT_DIR), uid = configFileDict["uid"], cmd = FILTER_CMD)
        if dryRun:
            print(SLURM_CMD)
        else:
            out = subprocess.check_output(SLURM_CMD, shell=True, universal_newlines= True, stderr=subprocess.STDOUT)
            BAM_FILTER_JID_LIST.append(catchJID(out))
            configFileDict['filtering_log_files'].append(getSlurmLog("{}/log".format(configFileDict["filtered_bam_dir"]),configFileDict['uid'],out))
    
    if dryRun:
        return "dryRun"
    else:
        FILTER_BAM_WAIT = ",".join(BAM_FILTER_JID_LIST)
        del BAM_FILTER_JID_LIST
        return FILTER_BAM_WAIT
    

 
def submitBAM2BW(configFileDict, BAM_FILES, dryRun=False):
    """[Submits jobs for removal of PCR duplicated reads]

    Args:
        configFileDict ([dict]): [configuration file dictionary]
        BAM_BW [str]: Absolute path where BAM FILES are and where to write them. 

    Returns:
        [str]: [Returns the slurm Job IDs so that the jobs of the next step can wait until mapping has finished]
    """
    BW_JID_LIST = []
    OUTPUT_DIR = configFileDict['bw_dir']
    for bam in BAM_FILES:
        input_file = os.path.basename(bam).split(".")[0]
        OUTPUT_FILE = "{}/{}.bw".format(OUTPUT_DIR, input_file)
        
        BAM2BW_CMD = "{bamcoverage} {arguments} --bam {input} -o {output}".format(bamcoverage=configFileDict['bamCoverage'], arguments=configFileDict['bam2bw'], input=bam, output=OUTPUT_FILE)
        
        if '4' in configFileDict['task_list']:
            SLURM_CMD = "{wsbatch} {slurm} -o {log_dir}/{uid}_slurm-%j.out --dependency=afterany:{JID} --wrap=\"{cmd}\"".format(wsbatch = configFileDict["wsbatch"], slurm = configFileDict["slurm_general"], log_dir = "{}/log".format(OUTPUT_DIR), uid = configFileDict["uid"], cmd = BAM2BW_CMD, JID=configFileDict['FILTER_BAM_WAIT'])
            #print(SLURM_CMD)
        elif configFileDict['technology'] == "RNAseq" and '2' in configFileDict['task_list']:
            SLURM_CMD = "{wsbatch} {slurm} -o {log_dir}/{uid}_slurm-%j.out --dependency=afterany:{JID} --wrap=\"{cmd}\"".format(wsbatch = configFileDict["wsbatch"], slurm = configFileDict["slurm_general"], log_dir = "{}/log".format(OUTPUT_DIR), uid = configFileDict["uid"], cmd = BAM2BW_CMD, JID=configFileDict['MAP_WAIT'])
        else:
            SLURM_CMD = "{wsbatch} {slurm} -o {log_dir}/{uid}_slurm-%j.out --wrap=\"{cmd}\"".format(wsbatch = configFileDict["wsbatch"], slurm = configFileDict["slurm_general"], log_dir = "{}/log".format(OUTPUT_DIR), uid = configFileDict["uid"], cmd = BAM2BW_CMD)
        
        if dryRun: 
            print(SLURM_CMD)
        else:
            out = subprocess.check_output(SLURM_CMD, shell=True, universal_newlines= True, stderr=subprocess.STDOUT)
            BW_JID_LIST.append(catchJID(out))
            configFileDict['bw_log_files'].append(getSlurmLog("{}/log".format(configFileDict["bw_dir"]),configFileDict['uid'],out))
            
    if dryRun:
        return "dryRun"
    else:    
        BAM2BW_WAIT = ",".join(BW_JID_LIST)
        del BW_JID_LIST
        return BAM2BW_WAIT
            
        
def submitBAM2BED(configFileDict, BAM_FILES, dryRun=False):
    """[Submits jobs for removal of PCR duplicated reads]

    Args:
        configFileDict ([dict]): [configuration file dictionary]
        BAM_BW [str]: Absolute path where BAM FILES are and where to write them. 

    Returns:
        [str]: [Returns the slurm Job IDs so that the jobs of the next step can wait until mapping has finished]
    """
    BAM2BED_JID_LIST = []
    OUTPUT_DIR = configFileDict['bed_dir']
    for bam in BAM_FILES:
        input_file = os.path.basename(bam).split(".")[0]
        OUTPUT_FILE = "{}/{}.bed".format(OUTPUT_DIR, input_file)
    
        BAM2BED_CMD = "source {bam2bed} {bedtools} {input} {output}".format(bedtools=configFileDict['bedtools'],bam2bed=configFileDict['bam2bed_script'],input=bam, output=OUTPUT_FILE)
        
        if '4' in configFileDict['task_list']: 
            SLURM_CMD = "{wsbatch} {slurm} -o {log_dir}/{uid}_slurm-%j.out --dependency=afterany:{JID} --wrap=\"{cmd}\"".format(wsbatch = configFileDict["wsbatch"], slurm = configFileDict["slurm_general"], log_dir = "{}/log".format(OUTPUT_DIR), uid = configFileDict["uid"], cmd = BAM2BED_CMD, JID=configFileDict['FILTER_BAM_WAIT'])
            #print(SLURM_CMD)
        else: 
            SLURM_CMD = "{wsbatch} {slurm} -o {log_dir}/{uid}_slurm-%j.out --wrap=\"{cmd}\"".format(wsbatch = configFileDict["wsbatch"], slurm = configFileDict["slurm_general"], log_dir = "{}/log".format(OUTPUT_DIR), uid = configFileDict["uid"], cmd = BAM2BED_CMD)
            #print(SLURM_CMD)
        
        if dryRun:
            print(SLURM_CMD)
        else:
            out = subprocess.check_output(SLURM_CMD, shell=True, universal_newlines= True, stderr=subprocess.STDOUT)
            BAM2BED_JID_LIST.append(catchJID(out))
            configFileDict['bam2bed_log_files'].append(getSlurmLog("{}/log".format(configFileDict["bed_dir"]),configFileDict['uid'],out))
            
    if dryRun:
        return "dryRun"
    else:   
        BAM2BED_WAIT = ",".join(BAM2BED_JID_LIST)
        del BAM2BED_JID_LIST
        return BAM2BED_WAIT

def submitExtendReads(configFileDict,BED_FILES, dryRun=False):
    """[Submits jobs for removal of PCR duplicated reads]

    Args:
        configFileDict ([dict]): [configuration file dictionary]
        BAM_BW [str]: Absolute path where BAM FILES are and where to write them. 

    Returns:
        [str]: [Returns the slurm Job IDs so that the jobs of the next step can wait until mapping has finished]
    """
    EXTENDBED_JID_LIST = []
    OUTPUT_DIR = configFileDict['extended_bed_dir']
    for bam in BED_FILES:
        input_file = os.path.basename(bam).split(".")[0]
        OUTPUT_FILE = "{}/{}.extendedReads.bed".format(OUTPUT_DIR, input_file)
        
        EXTENDBED_CMD = "source {BIN} {input} {extension} {genomeFileExtension} {output} {bedClip}".format(BIN=configFileDict['extendReadsScript'], extension=configFileDict['extend_reads'], input=bam, genomeFileExtension=configFileDict['genomeFileSize'], output=OUTPUT_FILE, bedClip = configFileDict['bedClip'])
        
        if '4' in configFileDict['task_list']: 
            SLURM_CMD = "{wsbatch} {slurm} -o {log_dir}/{uid}_slurm-%j.out --dependency=afterany:{JID} --wrap=\"{cmd}\"".format(wsbatch = configFileDict["wsbatch"], slurm = configFileDict["slurm_general"], log_dir = "{}/log".format(OUTPUT_DIR), uid = configFileDict["uid"], cmd = EXTENDBED_CMD, JID=configFileDict['BAM2BED_WAIT'])
        else: 
            SLURM_CMD = "{wsbatch} {slurm} -o {log_dir}/{uid}_slurm-%j.out --wrap=\"{cmd}\"".format(wsbatch = configFileDict["wsbatch"], slurm = configFileDict["slurm_general"], log_dir = "{}/log".format(OUTPUT_DIR), uid = configFileDict["uid"], cmd = EXTENDBED_CMD)
        
        if dryRun:
            print(SLURM_CMD)
        else:
            out = subprocess.check_output(SLURM_CMD, shell=True, universal_newlines= True, stderr=subprocess.STDOUT)
            EXTENDBED_JID_LIST.append(catchJID(out))
            configFileDict['extend_log_files'].append(getSlurmLog("{}/log".format(configFileDict["extended_bed_dir"]),configFileDict['uid'],out))
    
    if dryRun:
        return "dryRun"
    else:
        EXT_BED_WAIT = ",".join(EXTENDBED_JID_LIST)
        del EXTENDBED_JID_LIST
        return EXT_BED_WAIT


def submitPeakCalling(configFileDict,BED_FILES, dryRun=False):
    """[Submits jobs peak calling]

    Args:
        configFileDict ([dict]): [configuration file dictionary]
        BED_FILES [str]: Absolute path where BAM FILES are and where to write them. 

    Returns:
        [str]: [Returns the slurm Job IDs so that the jobs of the next step can wait until mapping has finished]
    """
    PEAK_CALLING_JID_LIST = []
    OUTPUT_DIR = configFileDict['peaks_dir']
    for bam in BED_FILES:
        input_file = os.path.basename(bam).split(".")[0]
        OUTPUT_FILE = "{}/{}.MACS".format(OUTPUT_DIR, input_file)
        
        PEAKCALL_CMD = "{macs2} callpeak {arguments} -t {input} -n {prefix} --outdir {output}".format(macs2=configFileDict['macs2'], arguments=configFileDict['peak_calling'], input=bam, output=OUTPUT_FILE, prefix=input_file)
        
        if '6' in configFileDict['task_list']: 
            SLURM_CMD = "{wsbatch} {slurm} -o {log_dir}/{uid}_slurm-%j.out --dependency=afterany:{JID} --wrap=\"{cmd}\"".format(wsbatch = configFileDict["wsbatch"], slurm = configFileDict["slurm_peakCalling"], log_dir = "{}/log".format(OUTPUT_DIR), uid = configFileDict["uid"], cmd = PEAKCALL_CMD, JID=configFileDict['EXT_BED_WAIT'])
        else: 
            SLURM_CMD = "{wsbatch} {slurm} -o {log_dir}/{uid}_slurm-%j.out --wrap=\"{cmd}\"".format(wsbatch = configFileDict["wsbatch"], slurm = configFileDict["slurm_general"], log_dir = "{}/log".format(OUTPUT_DIR), uid = configFileDict["uid"], cmd = PEAKCALL_CMD)
        
        if dryRun:
            print(SLURM_CMD)
        else:
            out = subprocess.check_output(SLURM_CMD, shell=True, universal_newlines= True, stderr=subprocess.STDOUT)
            PEAK_CALLING_JID_LIST.append(catchJID(out))
            configFileDict['peak_log_files'].append(getSlurmLog("{}/log".format(configFileDict["peaks_dir"]),configFileDict['uid'],out))
            
    if dryRun:
        return "dryRun"
    else:
        PEAK_CALLING_WAIT = ",".join(PEAK_CALLING_JID_LIST)
        del PEAK_CALLING_JID_LIST
        return PEAK_CALLING_WAIT


def submitChIPseqPeakCalling(configFileDict,BED_FILES, dryRun=False):
    """[Submits jobs peak calling]

    Args:
        configFileDict ([dict]): [configuration file dictionary]
        BED_FILES [str]: list of tuples containing bed file and inputs. 

    Returns:
        [str]: [Returns the slurm Job IDs so that the jobs of the next step can wait until mapping has finished]
    """
    PEAK_CALLING_JID_LIST = []
    OUTPUT_DIR = configFileDict['peaks_dir']
    
    for file in BED_FILES:
        sample = file[0]
        inputs = file[1]
        
        input_file = os.path.basename(sample).split(".")[0]
        OUTPUT_FILE = "{}/{}.MACS".format(OUTPUT_DIR, input_file)
        
        PEAKCALL_CMD = "{macs2} callpeak {arguments} -t {sample} -c {input} -n {prefix} --outdir {output}".format(macs2=configFileDict['macs2'], arguments=configFileDict['peak_calling'], input=inputs, sample = sample, output=OUTPUT_FILE, prefix=input_file)
        #print(PEAKCALL_CMD)
        if '6' in configFileDict['task_list']: 
            SLURM_CMD = "{wsbatch} {slurm} -o {log_dir}/{uid}_slurm-%j.out --dependency=afterany:{JID} --wrap=\"{cmd}\"".format(wsbatch = configFileDict["wsbatch"], slurm = configFileDict["slurm_peakCalling"], log_dir = "{}/log".format(OUTPUT_DIR), uid = configFileDict["uid"], cmd = PEAKCALL_CMD, JID=configFileDict['EXT_BED_WAIT'])
        else: 
            SLURM_CMD = "{wsbatch} {slurm} -o {log_dir}/{uid}_slurm-%j.out --wrap=\"{cmd}\"".format(wsbatch = configFileDict["wsbatch"], slurm = configFileDict["slurm_general"], log_dir = "{}/log".format(OUTPUT_DIR), uid = configFileDict["uid"], cmd = PEAKCALL_CMD)
        
        if dryRun:
            print(SLURM_CMD)
        else:
            out = subprocess.check_output(SLURM_CMD, shell=True, universal_newlines= True, stderr=subprocess.STDOUT)
            PEAK_CALLING_JID_LIST.append(catchJID(out))
            configFileDict['peak_log_files'].append(getSlurmLog("{}/log".format(configFileDict["peaks_dir"]),configFileDict['uid'],out))
    
    if dryRun:
        return "dryRun"
    else:    
        PEAK_CALLING_WAIT = ",".join(PEAK_CALLING_JID_LIST)
        del PEAK_CALLING_JID_LIST
        return PEAK_CALLING_WAIT



def submitPeak2Counts(configFileDict,NARROWPEAK_FILES,EXTENDED_BED_FILES, dryRun=False):
    """[Submits jobs peak2Counts]

    Args:
        configFileDict ([dict]): [configuration file dictionary]
        NARROWPEAK_FILES [str]: Absolute path where BAM FILES are and where to write them. 

    Returns:
        [str]: [Returns the slurm Job IDs so that the jobs of the next step can wait until mapping has finished]
    """
    
    OUTPUT_DIR = configFileDict['peakCounts_dir']
    
    PEAK2COUNT_CMD = "cat {files} | sort -k1,1 -k2,2n > {outputDir}/ALLsamples_peaks.bed &&  {bedtools} merge -i {outputDir}/ALLsamples_peaks.bed -d 1000 > {outputDir}/merged_peaks_ALLsamples.bed".format(files = " ".join(NARROWPEAK_FILES), outputDir = OUTPUT_DIR, bedtools = configFileDict['bedtools'], extendedBedFiles = " ".join(EXTENDED_BED_FILES))
    peak_cmd = []
    for bed in EXTENDED_BED_FILES: 
        outputFile = OUTPUT_DIR + "/" + os.path.basename(bed).replace("extendedReads.bed", "count")
        peak_cmd.append("{bedtools} intersect -a {outputDir}/merged_peaks_ALLsamples.bed -b {bed} -c > {outputFile}".format(bedtools = configFileDict['bedtools'], outputDir = OUTPUT_DIR, bed = bed, outputFile=outputFile))
    
    COMBINECOUNTS2BED_CMD = "python3 {combineCounts} --file-list {input_dir}/*.count --outputFile {input_dir}/AllSamples_chrALL.bed".format(combineCounts = configFileDict['combineCountScript'], input_dir = OUTPUT_DIR)
    
    CMDs = PEAK2COUNT_CMD + " && " + ";".join(peak_cmd) + " && " + COMBINECOUNTS2BED_CMD
    
    wait_condition = ""
     
    if '8' in configFileDict["task_list"] and '7' in configFileDict["task_list"]: 
        wait_condition = configFileDict['PEAK_CALLING_WAIT'] + "," + configFileDict['EXT_BED_WAIT']
    
    if '8' not in configFileDict["task_list"] and '7' not in configFileDict["task_list"]:
        SLURM_CMD = "{wsbatch} {slurm} -o {log_dir}/{uid}_slurm-%j.out --wrap=\"{cmd}\"".format(wsbatch = configFileDict["wsbatch"], slurm = configFileDict["slurm_general"], log_dir = "{}/log".format(OUTPUT_DIR), uid = configFileDict["uid"], cmd = CMDs)
    else:
        SLURM_CMD = "{wsbatch} {slurm} -o {log_dir}/{uid}_slurm-%j.out --dependency=afterany:{JID} --wrap=\"{cmd}\"".format(wsbatch = configFileDict["wsbatch"], slurm = configFileDict["slurm_general"], log_dir = "{}/log".format(OUTPUT_DIR), uid = configFileDict["uid"], cmd = CMDs, JID=wait_condition)
    #print(SLURM_CMD)
    if dryRun:
        print(SLURM_CMD)
    else:
        out = subprocess.check_output(SLURM_CMD, shell=True, universal_newlines= True, stderr=subprocess.STDOUT)
        PEAK_CALLING_JID_LIST = catchJID(out)
        configFileDict['peak2Count_log_files'].append(getSlurmLog("{}/log".format(configFileDict["peakCounts_dir"]),configFileDict['uid'],out))
    
    if dryRun:
        return "dryRun"
    else:
        PEAK_CALLING_WAIT = PEAK_CALLING_JID_LIST
        del PEAK_CALLING_JID_LIST
        return PEAK_CALLING_WAIT


def submitJobCheck(configFileDict, log_key, wait_key, dryRun=False):
    log_files = configFileDict[log_key]
    for file in log_files: 
        cmd = "python3 {jobCheck} -w -log {file}".format(jobCheck=configFileDict['jobCheck'], file=file)
        SLURM_CMD = "{wsbatch} --dependency=afterany:{JID} -o {raw_log}/slurm-%j.out --wrap=\"{cmd}\"".format(wsbatch=configFileDict['wsbatch'], cmd=cmd, JID=wait_key, raw_log = configFileDict['raw_log'])
        if dryRun:
            print(SLURM_CMD)
        else:
            out = subprocess.check_output(SLURM_CMD, shell=True, universal_newlines=True, stderr=subprocess.STDOUT)

def submitJobCheck2(configFileDict, logFiles, wait_key, dryRun=False):
    cmd = []
    for file in logFiles:
        cmd.append("python3 {jobCheck} -w -log {file}".format(jobCheck=configFileDict['jobCheck'], file=file))
    
    cmd = "; ".join(cmd)
    
    SLURM_CMD = "{wsbatch} --dependency=afterany:{JID} -o {raw_log}/slurm-%j.out --wrap=\"{cmd}\"".format(wsbatch=configFileDict['wsbatch'], cmd=cmd, JID=wait_key, raw_log = configFileDict['raw_log'])
    if dryRun:
        print(SLURM_CMD)
    else:
        out = subprocess.check_output(SLURM_CMD, shell=True, universal_newlines=True, stderr=subprocess.STDOUT)
        JOBCHECK_WAIT = catchJID(out)
        return JOBCHECK_WAIT

def submitATACseqQC(configFileDict, BAM_FILES, dryRun=False):
    ATACQC_JID_LIST = []
    OUTPUT_DIR = configFileDict['bamQC_dir']
    for bam in BAM_FILES:
        input_file = os.path.basename(bam).split(".")[0]
        
        ATACQC_CMD = "Rscript {BIN} {input} {output_dir}".format(BIN=configFileDict['ATACseqQC'],input = bam,output_dir = OUTPUT_DIR) 
        
        if '4' in configFileDict['task_list']:
            SLURM_CMD = "{wsbatch} {slurm} -o {log_dir}/{uid}_slurm-%j.out --dependency=afterany:{JID} --wrap=\"{cmd}\"".format(wsbatch = configFileDict["wsbatch"], slurm = configFileDict["slurm_general"], log_dir = "{}/log".format(OUTPUT_DIR), uid = configFileDict["uid"], cmd = ATACQC_CMD, JID=configFileDict['FILTER_BAM_WAIT'])
            #print(SLURM_CMD)
        else:
            SLURM_CMD = "{wsbatch} {slurm} -o {log_dir}/{uid}_slurm-%j.out --wrap=\"{cmd}\"".format(wsbatch = configFileDict["wsbatch"], slurm = configFileDict["slurm_general"], log_dir = "{}/log".format(OUTPUT_DIR), uid = configFileDict["uid"], cmd = ATACQC_CMD)
            #print(SLURM_CMD)
        
        if dryRun:
            print(SLURM_CMD)
        else:
            out = subprocess.check_output(SLURM_CMD, shell=True, universal_newlines= True, stderr=subprocess.STDOUT)
            ATACQC_JID_LIST.append(catchJID(out))
            configFileDict['atacQC_log_files'].append(getSlurmLog("{}/log".format(configFileDict["bamQC_dir"]),configFileDict['uid'],out))
        
    if dryRun: 
        return "dryRun"
    else:
        ATACQC_WAIT = ",".join(ATACQC_JID_LIST)
        del ATACQC_JID_LIST
        return ATACQC_WAIT




def submitBamQC(configFileDict, BAM_FILES, dryRun=False):
    BAMQC_JID_LIST = []
    OUTPUT_DIR = configFileDict['bamQC_dir']
    for bam in BAM_FILES:
        input_file = os.path.basename(bam).split(".")[0]
        
        output_file = f"{OUTPUT_DIR}/{input_file}_bamQC_stats.csv"
        BAMQC_CMD = "Rscript {BIN} {input} {output_dir}".format(BIN=configFileDict['ATACbamQC'],input = bam,output_dir = output_file) 
        
        if '4' in configFileDict['task_list']:
            SLURM_CMD = "{wsbatch} {slurm} -o {log_dir}/{uid}_slurm-%j.out --dependency=afterany:{JID} --wrap=\"{cmd}\"".format(wsbatch = configFileDict["wsbatch"], slurm = configFileDict["slurm_general"], log_dir = "{}/log".format(OUTPUT_DIR), uid = configFileDict["uid"], cmd = BAMQC_CMD, JID=configFileDict['FILTER_BAM_WAIT'])

        else:
            SLURM_CMD = "{wsbatch} {slurm} -o {log_dir}/{uid}_slurm-%j.out --wrap=\"{cmd}\"".format(wsbatch = configFileDict["wsbatch"], slurm = configFileDict["slurm_general"], log_dir = "{}/log".format(OUTPUT_DIR), uid = configFileDict["uid"], cmd = BAMQC_CMD)

        if dryRun:
            print(SLURM_CMD)
        else:
            out = subprocess.check_output(SLURM_CMD, shell=True, universal_newlines= True, stderr=subprocess.STDOUT)
            BAMQC_JID_LIST.append(catchJID(out))
            configFileDict['bamQC_log_files'].append(getSlurmLog("{}/log".format(configFileDict["bamQC_dir"]),configFileDict['uid'],out))
    
    combineCSV_cmd = "awk 'NR==1 || FNR>1 {{print}}' {outputDir}/*_bamQC_stats.csv > {outputDir}/Allsamples_bamQC_stats.csv".format(outputDir = OUTPUT_DIR)

    BAMQC_WAIT = ",".join(BAMQC_JID_LIST)
    SLURM_CMD = "{wsbatch} {slurm} -o {log_dir}/{uid}_slurm-%j.out --dependency=afterany:{JID} --wrap=\"{cmd}\"".format(wsbatch = configFileDict["wsbatch"], slurm = configFileDict["slurm_general"], log_dir = "{}/log".format(OUTPUT_DIR), uid = configFileDict["uid"], cmd = combineCSV_cmd, JID=BAMQC_WAIT)
    
    if dryRun:
        print(SLURM_CMD)
        return "dryRun"
    else:
        out = subprocess.check_output(SLURM_CMD, shell=True, universal_newlines= True, stderr=subprocess.STDOUT)
        BAMQC_WAIT += "," + catchJID(out)
        del BAMQC_JID_LIST
        return BAMQC_WAIT

def submitSamtoolsBamQC(configFileDict, BAM_FILES, dryRun=False):
    BAMQC_JID_LIST = []
    OUTPUT_DIR = configFileDict['bamQC_dir']
    for bam in BAM_FILES:
        sampleID = os.path.basename(bam).split(".")[0]
        
        
        if '4' in configFileDict['task_list']:
            ### CHECK THAT FILES ORIGINATE FROM BAM MARKED_BAM OR FILTERED_BAM
            bamDir = bam.split("/")[-2]
            if bamDir == "bam":
                prefix = f"sortedBam_{sampleID}"
            elif bamDir == "marked_bam":
                prefix = f"markedBam_{sampleID}"
            elif bamDir == "filtered_bam":
                prefix = f"filteredBam_{sampleID}"
            else:
                print("The bam directory is neither bam/marked_bam/filtered_bam. There is something wrong")
                sys.exit(-1)
        else:
            prefix = sampleID
        
        outputFile = f"{OUTPUT_DIR}/{prefix}_bamStats"
        BAMQC_CMD = "{samtools} stats {bam} > {outputFile}".format(samtools = configFileDict['samtools'], bam = bam, outputFile = outputFile, plotBam = configFileDict['plotBam'], input_file = prefix)
        
        if '4' in configFileDict['task_list']:
            SLURM_CMD = "{wsbatch} {slurm} -o {log_dir}/{uid}_slurm-%j.out --dependency=afterany:{JID} --wrap=\"{cmd}\"".format(wsbatch = configFileDict["wsbatch"], slurm = configFileDict["slurm_general"], log_dir = "{}/log".format(OUTPUT_DIR), uid = configFileDict["uid"], cmd = BAMQC_CMD, JID=configFileDict['FILTER_BAM_WAIT'])

        else:
            SLURM_CMD = "{wsbatch} {slurm} -o {log_dir}/{uid}_slurm-%j.out --wrap=\"{cmd}\"".format(wsbatch = configFileDict["wsbatch"], slurm = configFileDict["slurm_general"], log_dir = "{}/log".format(OUTPUT_DIR), uid = configFileDict["uid"], cmd = BAMQC_CMD)

        if dryRun:
            print(SLURM_CMD)
        else:
            out = subprocess.check_output(SLURM_CMD, shell=True, universal_newlines= True, stderr=subprocess.STDOUT)
            BAMQC_JID_LIST.append(catchJID(out))
            configFileDict['bamQC_log_files'].append(getSlurmLog("{}/log".format(configFileDict["bamQC_dir"]),configFileDict['uid'],out))
    
      
    BAMQC_WAIT = ",".join(BAMQC_JID_LIST)
    ## COMBINE ALL bamStats files together 
    COMBINE_CMD = "python3 {bamStatCombineScript} -f {outputDIR}/*_bamStats -out {outputDIR}/AllSamples_samtoolsStats.csv".format(bamStatCombineScript = configFileDict['combineBamStatScript'], outputDIR = OUTPUT_DIR)
    SLURM_CMD = "{wsbatch} {slurm} -o {log_dir}/{uid}_slurm-%j.out --dependency=afterany:{JID} --wrap=\"{cmd}\"".format(wsbatch = configFileDict["wsbatch"], slurm = configFileDict["slurm_general"], log_dir = "{}/log".format(OUTPUT_DIR), uid = configFileDict["uid"], cmd = COMBINE_CMD, JID=BAMQC_WAIT)
    
    if dryRun:
        print(SLURM_CMD)
        return "dryRun"
    else:
        out = subprocess.check_output(SLURM_CMD, shell=True, universal_newlines= True, stderr=subprocess.STDOUT)
        BAMQC_WAIT = BAMQC_WAIT + "," + catchJID(out)
        del BAMQC_JID_LIST
        return BAMQC_WAIT 

def submitFastQC(configFileDict, dryRun=False):
    FASTQC_JID_LIST = []
    OUTPUT_DIR = configFileDict['fastQC_dir']
    if '1' in configFileDict['task_list']: 
        DIRECTORIES = [configFileDict['fastq_dir'], configFileDict['trimmed_fastq_dir']]
    else:
        DIRECTORIES = [configFileDict['fastq_dir']]
    
    for DIR in DIRECTORIES:
        fastq_files = glob.glob(f"{DIR}/*fastq.gz")
        for fastq in fastq_files:
        
            FASTQC_CMD = "{fastqc} -o {output_dir} {fastq}".format(fastqc = configFileDict['FastQC'], output_dir = OUTPUT_DIR, fastq = fastq)
            if '1' in configFileDict['task_list']:
                SLURM_CMD = "{wsbatch} {slurm} -o {log_dir}/{uid}_slurm-%j.out --dependency=afterany:{JID} --wrap=\"{cmd}\"".format(wsbatch = configFileDict['wsbatch'], slurm = configFileDict['slurm_general'], log_dir = "{}/log".format(OUTPUT_DIR), uid = configFileDict['uid'],JID = configFileDict['TRIM_WAIT'], cmd = FASTQC_CMD)
                #print(SLURM_CMD)
            else: 
                SLURM_CMD = "{wsbatch} {slurm} -o {log_dir}/{uid}_slurm-%j.out --wrap=\"{cmd}\"".format(wsbatch = configFileDict['wsbatch'], slurm = configFileDict['slurm_general'], log_dir = "{}/log".format(OUTPUT_DIR), uid = configFileDict['uid'], cmd = FASTQC_CMD)
                #print(SLURM_CMD)
            
            if dryRun:
                print(SLURM_CMD)
            else:
                out = subprocess.check_output(SLURM_CMD, shell=True, universal_newlines= True, stderr=subprocess.STDOUT)
                FASTQC_JID_LIST.append(catchJID(out))
                configFileDict['fastqQC_log_files'].append(getSlurmLog("{}/log".format(configFileDict["fastQC_dir"]),configFileDict['uid'],out))
    
    if dryRun:
        return "dryRun"
    else:
        FASTQC_WAIT = ",".join(FASTQC_JID_LIST)
        del FASTQC_JID_LIST
        return FASTQC_WAIT

def submitMultiQC(configFileDict, dryRun=False):
    MFASTQC_JID_LIST = []
    INPUT_DIR = configFileDict['fastQC_dir']
    OUTPUT_DIR = INPUT_DIR
    cmd = "{multiqc} -s -o {output_dir} {input_dir}".format(multiqc = configFileDict['multiQC'],output_dir = OUTPUT_DIR, input_dir = INPUT_DIR)
    SLURM_CMD = "{wsbatch} {slurm} -o {log_dir}/{uid}_slurm-%j.out --dependency=afterany:{JID} --wrap=\"{cmd}\"".format(wsbatch = configFileDict['wsbatch'], slurm = configFileDict['slurm_general'], log_dir = "{}/log".format(OUTPUT_DIR), uid = configFileDict['uid'],JID = configFileDict['FASTQC_WAIT'], cmd = cmd)
    #print(SLURM_CMD)
    
    if dryRun:
        print(SLURM_CMD)
        return "dryRun"
    else:
        out = subprocess.check_output(SLURM_CMD, shell=True, universal_newlines= True, stderr=subprocess.STDOUT)
        MFASTQC_JID_LIST.append(catchJID(out))
                
        configFileDict['multiqc_log_files'].append(getSlurmLog("{}/log".format(configFileDict["fastQC_dir"]),configFileDict['uid'],out))
        
        MFASTQC_WAIT = ",".join(MFASTQC_JID_LIST)
        del MFASTQC_JID_LIST
        return MFASTQC_WAIT

def submitQTLtoolsExonQuantification(configFileDict, BAM_FILES, dryRun=False):
    QUANT_JID_LIST = []
    OUTPUT_DIR = configFileDict['quantification_dir']
    
    
    for bam in BAM_FILES: 
        sampleName = os.path.basename(bam).split(".")[0]
        outputFile = "{outputDir}/{smp}".format(outputDir = OUTPUT_DIR, smp = sampleName)
        #print(sampleName)
        #print(outputFile)
        
        QUAN_CMD = "{qtltools} quan --gtf {annotation} --bam {bam} --out-prefix {outputPrefix} --sample {smp} {quantOptions}".format(qtltools = configFileDict['QTLtools'], annotation = configFileDict['annotation'], bam = bam, outputPrefix = outputFile, smp = sampleName, quantOptions = configFileDict['quantOptions'])
        
        if '2' in configFileDict['task_list'] : 
           SLURM_CMD = "{wsbatch} {slurm} -o {log_dir}/{uid}_slurm-%j.out --dependency=afterany:{JID} --wrap=\"{cmd}\"".format(wsbatch = configFileDict['wsbatch'], slurm = configFileDict['slurm_general'], log_dir = "{}/log".format(OUTPUT_DIR), uid = configFileDict['uid'],JID = configFileDict['MAP_WAIT'], cmd = QUAN_CMD)
        else: 
            SLURM_CMD = "{wsbatch} {slurm} -o {log_dir}/{uid}_slurm-%j.out --wrap=\"{cmd}\"".format(wsbatch = configFileDict['wsbatch'], slurm = configFileDict['slurm_general'], log_dir = "{}/log".format(OUTPUT_DIR), uid = configFileDict['uid'],JID = configFileDict['MAP_WAIT'])
        
        if dryRun:
            print(SLURM_CMD)
        else:
            out = subprocess.check_output(SLURM_CMD, shell=True, universal_newlines= True, stderr=subprocess.STDOUT)
            QUANT_JID_LIST.append(catchJID(out))    
            configFileDict['quant_log_files'].append(getSlurmLog("{}/log".format(configFileDict["quantification_dir"]),configFileDict['uid'],out))
    
    if dryRun:
        return "dryRun"   
    else:
        QUANT_WAIT = ",".join(QUANT_JID_LIST)
        del QUANT_JID_LIST
        return QUANT_WAIT


def submitFeatureCountsGeneQuantification(configFileDict, BAM_FILES, dryRun=False):
    QUANT_JID_LIST = []
    OUTPUT_DIR = configFileDict['quantification_dir']
    
    
    for bam in BAM_FILES: 
        sampleName = os.path.basename(bam).split(".")[0]
        outputFile = "{outputDir}/{smp}".format(outputDir = OUTPUT_DIR, smp = sampleName)
        
        QUAN_CMD = "{bin} {quantOptions} -a {GTF} -o {outputFile}.raw.gene.count.txt {bamFile}".format(bin = configFileDict['featureCounts'], GTF = configFileDict['annotation'], outputFile = outputFile, bamFile = bam, quantOptions = configFileDict['quantOptions'])
        
        if '2' in configFileDict['task_list'] : 
            SLURM_CMD = "{wsbatch} {slurm} -o {log_dir}/{uid}_slurm-%j.out --dependency=afterany:{JID} --wrap=\"{cmd}\"".format(wsbatch = configFileDict['wsbatch'], slurm = configFileDict['slurm_general'], log_dir = "{}/log".format(OUTPUT_DIR), uid = configFileDict['uid'],JID = configFileDict['MAP_WAIT'], cmd = QUAN_CMD)
        else: 
            SLURM_CMD = "{wsbatch} {slurm} -o {log_dir}/{uid}_slurm-%j.out --wrap=\"{cmd}\"".format(wsbatch = configFileDict['wsbatch'], slurm = configFileDict['slurm_general'], log_dir = "{}/log".format(OUTPUT_DIR), uid = configFileDict['uid'])
        
        if dryRun:
            print(SLURM_CMD)
        else:    
            out = subprocess.check_output(SLURM_CMD, shell=True, universal_newlines= True, stderr=subprocess.STDOUT)
            QUANT_JID_LIST.append(catchJID(out))
            configFileDict['quant_log_files'].append(getSlurmLog("{}/log".format(configFileDict["quantification_dir"]),configFileDict['uid'],out))
       
    ### SUBMIT COMBINE QUANTIFICATIONS TO MULTI-SAMPLE BED FILE
    COMBINEQUAN = "python3 {combineQuan} --file-list {outputDir}/*.txt --outputFile Allsamples.chrALL.raw.gene.count.bed --gtf-file {gtfFile}".format(combineQuan = configFileDict['combineQuanScript'], outputDir = OUTPUT_DIR, gtfFile = configFileDict['annotation'])
    
    slurm_cmd = "{wsbatch} {slurm} -o {log_dir}/{uid}_slurm-%j.out --dependency=afterany:{JID} --wrap=\"{cmd}\"".format(wsbatch = configFileDict['wsbatch'], slurm = configFileDict['slurm_general'], log_dir = "{}/log".format(OUTPUT_DIR), uid = configFileDict['uid'],JID = ",".join(QUANT_JID_LIST), cmd = COMBINEQUAN) 
    
    if dryRun:
        print(SLURM_CMD)    
        return "dryRun"
    else:
        out = subprocess.check_output(slurm_cmd, shell=True, universal_newlines= True, stderr=subprocess.STDOUT)
        QUANT_JID_LIST.append(catchJID(out))
        QUANT_WAIT = ",".join(QUANT_JID_LIST)
        del QUANT_JID_LIST
        return QUANT_WAIT
