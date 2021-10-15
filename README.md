
![](BraunLabPipeline.png)

# Pipeline for High-throughput sequencing data.

This pipeline allows to process ATAC-/ChIP- or RNA-seq data from fastq to peak calls / gene expression.


# Table of contents
1. [How to use the pipeline](#introduction)
2. [Steps of the pipeline](#steps)
   1. [Step 1: Trimming Reads](#step1)
      1. [Step 1.1: QC of fastq files](#step1_1)
   2. [Step 2: Mapping reads](#step2)
   3. [Step3: Marking duplicated reads](#step3)
   4. [Step4: Filtering reads](#step4)
      1. [Step4.1: Fragment Size distribution](#step4_1)
      2. [Step4.2: Bam QC](#step4_2)
   5. [Step5: BAM to BW](#step5)
   6. [Step6: Bam to Bed](#step6)
   7. [Step7: Read extension](#step7)
   8. [Step8: Peak calling](#step8)
   9. [Step8.1: Peak to counts](#step8_1)
   10. [Step9: Gene quantification](#step9)
3.  [Filename convention](#name_convention)
4.  [Running the pipeline](#howToRun)


## How to use the pipeline <a name="introduction"></a>

```bash 
python3 main.py --help
#The following command outputs how to use the script. 
usage: main.py [-h] [-v] -raw RAW_DIR [-fastq FASTQ_DIR] [-bam BAM_DIR]
               [-peak PEAKS_DIR] [-eqd EQ_DIR] [-bed BED_DIR] [-bw BIGWIG_DIR]
               [-od OUTPUT_DIR] -cf CONFIG_FILE_PATH -t TASK [TASK ...]

BraunPipeline
 *  Authors     : Nikolaos Lykoskoufis / Simon Braun
 *  Contact     : nikolaos.lykoskoufis@unige.ch / simon.braun@unige.ch
 *  Webpage     : https://github.com/NLykoskoufis/braunATACpipeline
 *  Version     : 1.0
 *  Description : Pipeline to process High throughput sequencing data.

optional arguments:
  -h, --help            show this help message and exit
  -v                    Display pipeline version
  -raw RAW_DIR, --raw-dir RAW_DIR
                        Absolute path to the raw directory
  -fastq FASTQ_DIR, --fastq-dir FASTQ_DIR
                        Absolut path fastq to diretor(y)ies. If multiple directories, separate eache path with space
  -bam BAM_DIR, --bam-dir BAM_DIR
                        Path bam diretory, is multiple, separate with space.
  -peak PEAKS_DIR, --peak-dir PEAKS_DIR
                        Path peak diretory, is multiple, separate with space.
  -eqd EQ_DIR, --quant-dir EQ_DIR, -quantification_dir EQ_DIR
                        Absolut path quantifications diretory
  -bed BED_DIR, --bed-dir BED_DIR
                        Absolut path of where to save/read bed files
  -bw BIGWIG_DIR, --bigwig-dir BIGWIG_DIR
                        Absolut path peak calling diretory
  -od OUTPUT_DIR, --output-dir OUTPUT_DIR
                        Path to output directory. Use it only if you do not run the pipeline from step
  -cf CONFIG_FILE_PATH, --configuration-file CONFIG_FILE_PATH
                        Name of your configuration file: project_run_config_V1
  -t TASK [TASK ...], --task TASK [TASK ...]
```
The different arguments of the pipeline are: 

| Argument | Definition |
|:---:|:-------------------------------------------:|
| **-cf**  | Absolute path to the configuration file |
| **-raw** | Absolute path to the raw directory |
| -od | Absolute path to the output directory | 
| -fastq | Abolute path to the fastq directory | 
| -bam | Absolute path to the bam directory | 
| -eqd | Absolute path to the quantification directory | 
| -bed | Absolute path to the bed directory | 
| -bw | Absolute path to the bigwid directory | 
| **-t** | Tasks to be ran. It can be an integer from 1 to 8 or "all" which specifies run all steps |

The arguments in bold are required for the pipeline no matter whether you run all the steps or specific steps. 

The **configuration file** contains all the necessary paths to software and all the parameters you want to use for each task. Below is an snippet of the configuration file. 
```

#### ANNOTATION FILES #####
#annotation, /srv/beegfs/scratch/groups/funpopgen/data/annotations/gencode.v19.annotation.nochr.gtf
annotation,/srv/beegfs/scratch/shares/brauns_lab/data/annotations/mus_musculus/Mus_musculus.GRCm38.102.modified.txt
###########################

#### PAIRED-END or NOT ####
#Are reads Pair-end read: 1 if they are pair-end, 0 if they are single-end
pairend,0
############################

# Are you mapping ATAC-seq, ChIP-seq or RNAseq data?
technology,RNAseq

#### READ TRIMMING OPTIONS ####
#Example of how a cutadapt commands looks like
#cutadapt -a CTGTCTCTTATACACATCTCCGAGCCCACGAGAC -A CTGTCTCTTATACACATCTGACGCTGCCGACGA -m 20 -O 5 -o testFile_R1_001.trim.fastq.gz -p testFile_R2_001.trim.fastq.gz testFile_R1_001.fastq.gz testFile_R2_001.fastq.gz
#If you want to modify the parameters used, you can comment the line below, and add what you want.
trim_reads, -a CTGTCTCTTATACACATCTCCGAGCCCACGAGAC -A CTGTCTCTTATACACATCTGACGCTGCCGACGA -m 20 -O 5
###############################

#### MAPPER ####
#Choose your mapper (possible options: STAR, bwa, bowtie,HiSat2, etc...)
mapper,STAR
#mapper,bowtie2
################
```

All lines starting with a **#** are not read by the pipeline. 

The lines that the pipeline are read need to be specially formatted. They should always start with a keyword, as follows: 
**keyword, parameters to use**

Keywords are essential in the configuration file because they are recognised by the pipeline as is. 

#Steps of the pipeline <a name="steps"></a>

### Task 1: Trimming of reads <a name="step1"></a>

### Task 1.1: QC of fastq files <a name="step1_1"></a>

### Task 2: Mapping <a name="step2"></a>

The mapping software compatible with the pipeline are: 

- STAR (RNAseq data)
- bowtie2 (ChIP-seq / ATAC-seq)

### Task 3: Marking duplicated reads <a name="step3"></a>

This step is not used for RNA-seq data processing since removal of duplicated reads. 

### Task 4: Filtering low quality read & MT reads & duplicates <a name="step4"></a>

This step is only used for ChIP-seq or ATAC-seq data.

### Task 4.1: Fragment size distribution QC <a name="step4_1"></a>

This task is reserved for ATAC-seq data. 

### Task 4.2: QC of bam files. <a name="step4_2"></a>

### Task 5: Bam to BW <a name="step5"></a>

### Task 6: Bam to Bed <a name="step6"></a>

This step is reserved for ChIP-seq and ATAC-seq data.

### Task 7: Read extension <a name="step7"></a>

This step is reserved for ChIP-seq and ATAC-seq data. 

### Task 8: Peak calling <a name="step8"></a>

This step is reserved for ChIP-seq and ATAC-seq data. 

### Task 8.1: Peak quantification <a name="step8_1"></a>

This step is reserved for ChIP-seq and ATAC-seq data. 

For each sample, we concatenate all peaks into a single annotation bed file. We then merge peaks that are up to 1kb far away. Then, we count for each sample, the reads overlapping each peak. 

### Task 9: Gene quantification <a name="step9"></a>

This step is reserved for RNA-seq data.


## File naming convention <a name="name_convention"></a>

**This is very important!!!**
##### Fastq files
Fastq files should be written in this specific way: 

SampleID*.R1_*.fastq.gz
and if paired-end data:
SampleID*.R2_*.fastq.gz 

If you use ChIP-seq, the input files should be written as follows: 

Input_SampleID*.R1_*.fastq.gz

***If you do not respect the naming convention, the pipeline will FAIL***

All other files should start with SampleID.whatever and Input_SampleID.whatever (if ChIP-seq data).


# Running the pipeline <a name="howToRun"></a>

You have the option to run all tasks of the pipeline or specify which steps you want to run. If you run the whole pipeline in one go, then you need to specify the --task; --raw-dir; --fastq-dir; -cf
; parameters. 

Otherwhise, depending on the tasks you decide to run, you will need to use different combination of parameters. For example to convert bam files to bed files you will need to use --task; --raw-dir; --bam-dir; -cf. Or if you want to run task 8 (peak calling), then you need to use --task; --raw-dir; --bed-dir; -cf.


### Directory tree generated by pipeline 

```bash 
raw_dir
├── ATACseqQC
│   └── log
├── bam
│   └── log
├── bed
│   └── log
├── bigwig
│   └── log
├── extended_bed
│   └── log
├── fastq
├── fastQC
│   ├── log
│   └── multiqc_data
├── filtered_bam
│   └── log
├── log
├── marked_bam
│   └── log
├── peaks
│   └── log
├── report
│   └── log
├── sorted_bam
│   └── log
└── trimmed_fastq
    └── log
```
