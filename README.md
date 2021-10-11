
![](Pipeline.png)

## Pipeline for High-throughput sequencing data.

This pipeline allows to process ATAC-/ChIP- or RNA-seq data from fastq to peak calls / gene expression.

## How to use the pipeline 

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

All lines starting with a # are not read by the pipeline. 

The lines that the pipeline are read need to be specially formated. They should always start with a keyword, as follows: 
**keyword, parameters to use**

Be careful to write the keyword correctly otherwhise the pipeline will not work!


##Steps of the pipeline 

#### Trimming reads 

This step trims the reads using cutadapt. 

#### Mapping reads 

This step maps reads. Depending whether you have ATAC-seq/ChIP-seq or RNAseq data, the mapper will be different. 

#### Sort bam files by coordinates. 
This step has to be done because PICARD requires sorted by coordinate bam files. 

#### Mark PCR duplicates
This step marks duplicated reads using PICARD.

#### Filtering, sorting and indexing bam file
This step removes duplicated reads, low quality reads, chrM the bam files. Then it sorts and index. 

#### CREATE .bw for visualization.
This step reads the bam files and created .bw files for visualization using IGV for exmample.

#### bam2bed 
This step converts bam files to UCSC bed files. 

#### Bed file with extended reads 
This step extends the reas on the bed files depending on the given extension provided

#### PEAK Calling
This step performs peak calling using MACS2. This is a step unique to ATAC-seq or ChIP-seq data.

#### Exon quantification
TBD

## File naming convention

**This is very important!!!**
##### Fastq files
Fastq files should be written in this specific way: 
SampleID*.R1_*.fastq.gz
SampleID*.R2_*.fastq.gz 
The pipeline will split the filename by "." and take as sampleID the first element which in our example is "SampleID". Then it will look for the R1 or R2 and the fastq.gz. If your fastq files are not written this way the pipeline will FAIL. 

##### Bam Files
Bam files need to be written as following: 
sampleID.*.bam 
The asterisk can be whatever. The pipeline splits the file name by "." and takes the first element as sampleID in this case the sample ID is "sampleID" and disregards the rest. 


##### Running the whole pipeline 
If you run the whole pipeline, then you need to specify: 
-cf
-raw 
-t 
-fastq

The pipeline will read the configuration file and run all steps and save the results under the raw directory given. No need to specify the directories, they are automatically created by the pipeline. IF the raw directory contains any of the other directories that will be created automatically by the pipeline, then it throws an error. For example if you already had created the bam directory under the raw directory, the pipeline will throw an error stating that the bam directory already exists and will stop. This is to prevent overwriting or erasing files by mistake. 

##### Running step 1
```bash 
python3 main.py -cf -raw -fastq -t
```
##### Running step 1.1

```bash 
python3 main.py -cf -raw -fastq -t
```

##### Running step 2 or from step 2
```bash 
python3 main.py -cf -raw  -fastq -od -t
```
##### Running step 3 or from step 3
```bash 
python3 main.py 
    -cf 
    -raw
    -bam 
    -od
    -t 
```
##### Running step 4 or from step 4
```bash 
python3 main.py
    -cf 
    -raw 
    -bam 
    -od 
    -t 
```

##### Running step 4.1 or from step 4
```bash 
python3 main.py
    -cf 
    -raw 
    -bam 
    -od 
    -t 
```

##### Running step 5 or from step 5
```bash 
python3 main.py
    -cf 
    -raw 
    -bam 
    -od 
    -t 
```
##### Running step 6 or from step 6
```bash 
python3 main.py
    -cf 
    -raw 
    -bam 
    -od 
    -t 
```
##### Running step 7 or from step 7
```bash 
python3 main.py
    -cf 
    -raw 
    -bed
    -od 
    -t
```
##### Running step 8 or from step 8
```bash 
python3 main.py 
    -cf
    -raw 
    -bed 
    -d 
    -t 
```

#### Directory tree generated by pipeline

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
