#!/usr/bin/env python3 

import subprocess
import sys 
import glob
import os

pipeline_path = sys.path[0]
pipeline_tools_path = os.path.abspath(pipeline_path + "/pipeline_tools")
sys.path.append(pipeline_tools_path)
from slurmTools import catchJID

def submitTrimming(configFileDict, FASTQ_PREFIX):
    TRIM_JID_LIST = []
    for file in FASTQ_PREFIX:
        TRIM_CMD = "{bin} {parameters} -o {trimmed_dir}/{file}.trim_R1_001.fastq.gz -p {trimmed_dir}/{file}.trim_R2_001.fastq.gz {fastq_dir}/{file}_R1_001.fastq.gz {fastq_dir}/{file}_R2_001.fastq.gz".format(bin=configFileDict["cutadapt"], parameters=configFileDict["trim_reads"], file=file, trimmed_dir = configFileDict["trimmed_fastq_dir"], fastq_dir=configFileDict['fastq_dir'])
        SLURM_CMD = "{wsbatch} {slurm} -o {trimmed_log_dir}/{uid}_slurm-%j.out --wrap=\"{cmd}\"".format(wsbatch = configFileDict["wsbatch"], slurm = configFileDict["slurm_trim"], trimmed_log_dir = "{}/log".format(configFileDict["trimmed_fastq_dir"]), uid = configFileDict["uid"], cmd = TRIM_CMD)
        print(SLURM_CMD)
        out = subprocess.check_output(SLURM_CMD, shell=True, universal_newlines= True, stderr=subprocess.STDOUT)
        TRIM_JID_LIST.append(catchJID(out))
        #TRIM_JID_LIST.append('0') #### FOR DEBUGGING PURPOSES
        
    TRIM_WAIT = ",".join(TRIM_JID_LIST)
    del TRIM_JID_LIST
    return TRIM_WAIT


def submitMappingBowtie(configFileDict, FASTQ_PREFIX, FASTQ_PATH):
    """[Submits jobs for Mapping using Bowtie2]

    Args:
        configFileDict ([dict]): [configuration file dictionary]
        FASTQ_FILES ([lst]): [List containing the FASTQ sample IDs]
        FASTQ_PATH [str]: Absolute path of the FASTQ files
    Returns:
        [str]: [Returns the slurm Job IDs so that the jobs of the next step can wait until mapping has finished]
    """    
    for file in FASTQ_PREFIX:                                                        
        MAP_JID_LIST = []
        MAP_CMD = "{mapper} {parameters} -x {REFSEQ} -1 {dir}/{file}*_R1_001.fastq.gz -2 {dir}/{file}*_R2_001.fastq.gz | {samtools} view -b -h -o {bam_dir}/{file}.bam".format(mapper=configFileDict['bowtie2'], parameters=configFileDict['bowtie_parameters'],dir=FASTQ_PATH,file=file, samtools = configFileDict["samtools"], bam_dir=configFileDict['bam_dir'], REFSEQ=configFileDict['reference_genome'])
        if '1' in configFileDict['task_list']: 
            SLURM_CMD = "{wsbatch} {slurm} -o {log_dir}/{uid}_slurm-%j.out --dependency=afterok:{JID} --wrap=\"{cmd}\"".format(wsbatch = configFileDict["wsbatch"], slurm = configFileDict["slurm_mapping"], log_dir = "{}/log".format(configFileDict['bam_dir']), uid = configFileDict["uid"], cmd = MAP_CMD, JID=configFileDict["TRIM_WAIT"])
            print(SLURM_CMD)
        else: 
            SLURM_CMD = "{wsbatch} {slurm} -o {log_dir}/{uid}_slurm-%j.out --wrap=\"{cmd}\"".format(wsbatch = configFileDict["wsbatch"], slurm = configFileDict["slurm_mapping"], log_dir = f"{configFileDict['bam_dir']}/log", uid = configFileDict["uid"], cmd = MAP_CMD)
            print(SLURM_CMD)
        out = subprocess.check_output(SLURM_CMD, shell=True, universal_newlines= True, stderr=subprocess.STDOUT)
        MAP_JID_LIST.append(catchJID(out))
                
    MAP_WAIT = ",".join(MAP_JID_LIST)
    del MAP_JID_LIST
    return MAP_WAIT


def submitFilteringBAM(configFileDict, BAM_PREFIX,BAM_PATH):
    """[Submits jobs for filtering and sorting BAM files]

    Args:
        configFileDict ([dict]): [configuration file dictionary]
        BAM_FILES ([lst]): [List containing the BAM files]

    Returns:
        [str]: [Returns the slurm Job IDs so that the jobs of the next step can wait until mapping has finished]
    """
    BAM_FILTER_JID_LIST = []
    for bam in BAM_PREFIX:
        INPUT_FILE = "{}.bam".format(bam)
        OUTPUT_FILE = "{}.QualTrimNoMt.bam".format(os.path.basename(bam))
        print(OUTPUT_FILE)
        
        FILTER_CMD = "{samtools} view {parameters} {bam_dir}/{file} | awk '{{if(\$3!~/chr[MT]/) {{print}}}}' | {samtools} sort -O BAM -T {sorted_bam_dir}/{output} -o {sorted_bam_dir}/{output}".format(samtools=configFileDict["samtools"], parameters=configFileDict['filter_bam'], bam_dir=BAM_PATH, file=INPUT_FILE, sorted_bam_dir=configFileDict["sorted_bam_dir"], output=OUTPUT_FILE)
        print(FILTER_CMD)
        if '2' in configFileDict['task_list']: 
            SLURM_CMD = "{wsbatch} {slurm} -o {log_dir}/{uid}_slurm-%j.out --dependency=afterok:{JID} --wrap=\"{cmd}\"".format(wsbatch = configFileDict["wsbatch"], slurm = configFileDict["slurm_general"], log_dir = "{}/log".format(configFileDict['sorted_bam_dir']), uid = configFileDict["uid"], cmd = FILTER_CMD, JID=configFileDict['MAP_WAIT'])
        else: 
            SLURM_CMD = "{wsbatch} {slurm} -o {log_dir}/{uid}_slurm-%j.out --wrap=\"{cmd}\"".format(wsbatch = configFileDict["wsbatch"], slurm = configFileDict["slurm_general"], log_dir = "{}/log".format(configFileDict['sorted_bam_dir']), uid = configFileDict["uid"], cmd = FILTER_CMD)
            
        out = subprocess.check_output(SLURM_CMD, shell=True, universal_newlines= True, stderr=subprocess.STDOUT)
        BAM_FILTER_JID_LIST.append(catchJID(out))
    
    FILTER_BAM_WAIT = ",".join(BAM_FILTER_JID_LIST)
    del BAM_FILTER_JID_LIST
    return FILTER_BAM_WAIT
    


def submitPCRduplication(configFileDict, BAM_FILES,BAM_PATH):
    """[Submits jobs for marking PCR duplicated reads using PICARD]

    Args:
        configFileDict ([dict]): [configuration file dictionary]
        BAM_PATH ([lst]): [List containing the BAM file absolute path]

    Returns:
        [str]: [Returns the slurm Job IDs so that the jobs of the next step can wait until mapping has finished]
    """
    PCR_DUP_JID_LIST = []
    for bam in BAM_FILES:
        OUTPUT_FILE = bam.replace(".QualTrimNoMt.bam",".QualTrimNoMt.Picard.bam")
        METRIX_FILE = bam.replace(".QualTrimNoMt.bam", "metrix")
        
        PCR_CMD = "{PICARD} MarkDuplicates I={input} O={output} M={metrix}".format(PICARD=configFileDict['PICARD'], input=bam, output=OUTPUT_FILE, metrix=METRIX_FILE)
        if '3' in configFileDict['task_list']:
            SLURM_CMD = "{wsbatch} {slurm} -o {log_dir}/{uid}_slurm-%j.out --dependency=afterok:{JID} --wrap=\"{cmd}\"".format(wsbatch = configFileDict["wsbatch"], slurm = configFileDict["slurm_general"], log_dir = "{}/log".format(BAM_PATH), uid = configFileDict["uid"], cmd = PCR_CMD, JID=configFileDict['FILTER_BAM_WAIT'])
        else: 
            SLURM_CMD = "{wsbatch} {slurm} -o {log_dir}/{uid}_slurm-%j.out --wrap=\"{cmd}\"".format(wsbatch = configFileDict["wsbatch"], slurm = configFileDict["slurm_general"], log_dir = "{}/log".format(BAM_PATH), uid = configFileDict["uid"], cmd = PCR_CMD)
    PCR_DUPLICATION_WAIT = ",".join(PCR_DUP_JID_LIST)
    del PCR_DUP_JID_LIST 
    return PCR_DUPLICATION_WAIT
            

def submitPCRremoval(configFileDict, BAM_PATH):
    """[Submits jobs for removal of PCR duplicated reads]

    Args:
        configFileDict ([dict]): [configuration file dictionary]
        BAM_PATH [str]: Absolute path where BAM FILES are and where to write them. 

    Returns:
        [str]: [Returns the slurm Job IDs so that the jobs of the next step can wait until mapping has finished]
    """ 
    PCR_REMOVAL_JID_LIST = []
    BAM_FILES = glob.glob("{}/*.Picard.bam".format(BAM_PATH))
    for bam in BAM_FILES:
        OUTPUT_FILE = bam.replace(".Picard.bam",".NoDup.bam")
        RMP_CMD = "{samtools} {parameters} {input} -o {output} ".format(samtools=configFileDict['samtools'], parameters=configFileDict['PCR_duplicates_removal'], input=bam, output=OUTPUT_FILE)
        if '4' in configFileDict['task_list']:
            SLURM_CMD = "{wsbatch} {slurm} -o {log_dir}/{uid}_slurm-%j.out --dependency=afterok:{JID} --wrap=\"{cmd}\"".format(wsbatch = configFileDict["wsbatch"], slurm = configFileDict["slurm_general"], log_dir = "{}/log".format(BAM_PATH), uid = configFileDict["uid"], cmd = RMP_CMD, JID=configFileDict['PCR_DUPLICATION_WAIT'])
        else: 
            SLURM_CMD = "{wsbatch} {slurm} -o {log_dir}/{uid}_slurm-%j.out --wrap=\"{cmd}\"".format(wsbatch = configFileDict["wsbatch"], slurm = configFileDict["slurm_general"], log_dir = "{}/log".format(BAM_PATH), uid = configFileDict["uid"], cmd = RMP_CMD)
    PCR_REMOVAL_WAIT = ",".join(PCR_REMOVAL_JID_LIST)
    del PCR_REMOVAL_JID_LIST
    return PCR_REMOVAL_WAIT


def submitIndexingBAM(configFileDict, BAM_PATH):
    """[Submits jobs for removal of PCR duplicated reads]

    Args:
        configFileDict ([dict]): [configuration file dictionary]
        BAM_PATH [str]: Absolute path where BAM FILES are and where to write them. 

    Returns:
        [str]: [Returns the slurm Job IDs so that the jobs of the next step can wait until mapping has finished]
    """
    INDEX_JID_LIST = []
    BAM_FILES = glob.glob("{}/*.bam".format(BAM_PATH))
    for bam in BAM_FILES:
        INDEX_CMD = "{samtools} index {input}".format(samtools=configFileDict['samtools'], input=bam)
        if '5' in configFileDict['task_list']: 
            SLURM_CMD = "{wsbatch} {slurm} -o {log_dir}/{uid}_slurm-%j.out --dependency=afterok:{JID} --wrap=\"{cmd}\"".format(wsbatch = configFileDict["wsbatch"], slurm = configFileDict["slurm_general"], log_dir = "{}/log".format(BAM_PATH), uid = configFileDict["uid"], cmd = INDEX_CMD, JID=configFileDict['PCR_REMOVAL_WAIT'])
        else:
            SLURM_CMD = "{wsbatch} {slurm} -o {log_dir}/{uid}_slurm-%j.out --wrap=\"{cmd}\"".format(wsbatch = configFileDict["wsbatch"], slurm = configFileDict["slurm_general"], log_dir = "{}/log".format(BAM_PATH), uid = configFileDict["uid"], cmd = INDEX_CMD)
    INDEXING_BAM_WAIT = ",".join(INDEX_JIS_LIST)
    del INDEX_JID_LIST
    return INDEXING_BAM_WAIT


def submitBam2bw(configFileDict, BAM_BW):
    """[Submits jobs for removal of PCR duplicated reads]

    Args:
        configFileDict ([dict]): [configuration file dictionary]
        BAM_BW [str]: Absolute path where BAM FILES are and where to write them. 

    Returns:
        [str]: [Returns the slurm Job IDs so that the jobs of the next step can wait until mapping has finished]
    """
    BW_JID_LIST = []
    BAM_FILES = glob.glob("{}/*.bam".format(BAM_BW))
    for bam in BAM_FILES:
        #bamCoverage --bam ${file}.NoDup.bam --binSize 10 --normalizeUsing RPKM --ignoreForNormalization chrM ChrUn ChrRandom --numberOfProcessors max -o ${file}.RPKMNorm.bw

        BW_CMD = "{bin} {parameters} --bam {input}"
        
        
def submitBam2Bed(configFileDict, BAM_PATH):
    """[Submits jobs for removal of PCR duplicated reads]

    Args:
        configFileDict ([dict]): [configuration file dictionary]
        BAM_BW [str]: Absolute path where BAM FILES are and where to write them. 

    Returns:
        [str]: [Returns the slurm Job IDs so that the jobs of the next step can wait until mapping has finished]
    """
    BAM2BED_JID_LIST = []
    BAM_FILES = glob.glob("{}/*.bam".format(BAM_PATH))
    for bam in BAM_FILES:
        BAM2BED_CMD = "{bedtools} bamtobed -i {input} | awk -F '\t' '{{print \$1,\$2,\$3,\$3-\$2,\$5,\$6}}' > {output}".format(bedtools=configFileDict['bedtools'], input=bam, output=os.path.basename(bam).replace(".bam",".bed"))
        if '6' in configFileDict['task_list']: 
            SLURM_CMD = "{wsbatch} {slurm} -o {log_dir}/{uid}_slurm-%j.out --dependency=afterok:{JID} --wrap=\"{cmd}\"".format(wsbatch = configFileDict["wsbatch"], slurm = configFileDict["slurm_general"], log_dir = "{}/log".format(configFileDict['bed_dir']), uid = configFileDict["uid"], cmd = BAM2BED_CMD, JID=configFileDict['INDEXING_BAM_WAIT'])
        else: 
            SLURM_CMD = "{wsbatch} {slurm} -o {log_dir}/{uid}_slurm-%j.out --wrap=\"{cmd}\"".format(wsbatch = configFileDict["wsbatch"], slurm = configFileDict["slurm_general"], log_dir = "{}/log".format(configFileDict['bed_dir']), uid = configFileDict["uid"], cmd = BAM2BED_CMD)
    BAM2BED_WAIT = ",".join(BAM2BED_JID_LIST)
    del BAM2BED_JID_LIST
    return BAM2BED_WAIT

def submitExtendReads(configFileDict):
    """[Submits jobs for removal of PCR duplicated reads]

    Args:
        configFileDict ([dict]): [configuration file dictionary]
        BAM_BW [str]: Absolute path where BAM FILES are and where to write them. 

    Returns:
        [str]: [Returns the slurm Job IDs so that the jobs of the next step can wait until mapping has finished]
    """