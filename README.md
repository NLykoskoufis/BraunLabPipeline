
                            ########   ########       ##      ##    ## ##     ## ## ########
                            ##     ##  ##     ##     ## ##    ##    ## ###    ##    ##
                            #######    ########     ##   ##   ##    ## ## ##  ##    ########
                            ##     ##  ##     ##   ## ### ##  ##    ## ##  ## ##          ## 
                            ########   ##      ## ##       ##  ######  ##    ###    ########      

                            ########  ##  ########  ########  ##       ##  ##     ##  ########
                            ##    ##  ##  ##    ##  ##        ##       ##  ###    ##  ##
                            #######   ##  #######   ######    ##       ##  ## ##  ##  ######
                            ##        ##  ##        ##        ##       ##  ##  ## ##  ##
                            ##        ##  ##        ########  ######## ##  ##    ###  ########


# BraunPipeline 
## Pipeline for processing ATACseq, ChIPseq and RNAseq data from fastq to peak counts / gene expression.

This is a document explaining how the pipeline works.
The pipeline is split in multiple steps. Depending on the type of data you are using, different steps will be ran. 

The pipeline works with a configuration file that contains all the paths for the software to be used and the different commands to be used per step. 

You can run the whole pipeline or specify which step(s) you want to run.

## How to use the pipeline 

```bash 
python3 main.py --help
#The following command outputs how to use the script. 
#usage: main.py [-h] [-v] [-fastq FASTQ_DIR] [-trimfastq TRIMMED_FASTQ_DIR]
#               [-bam BAM_DIR] [-sortedBam SORTED_BAM_DIR] [-eqd EQ_DIR]
#               [-bed BED_DIR] [-bw BIGWIG_DIR] [-od OUTPUT_DIR] -cf
#               CONFIG_FILE_PATH [-tf] [-tb] -t TASK [TASK ...]

#Pipeline to process data from illumina sequencers.

#optional arguments:
#  -h, --help            show this help message and exit
#  -v                    Display pipeline version
#  -fastq FASTQ_DIR, -fastqdir FASTQ_DIR
#                        Absolut path fastq to diretor(y)ies. If multiple
#                        directories, separate eache path with space
#  -bam BAM_DIR, -bamdir BAM_DIR
#  -eqd EQ_DIR, -quantification_dir EQ_DIR
#                        Absolut path peak calling diretory
#  -bed BED_DIR, -bed BED_DIR
#                        Absolut path of where to save/read bed files
#  -bw BIGWIG_DIR, -bigwig BIGWIG_DIR
#                        Absolut path peak calling diretory
#  -od OUTPUT_DIR, -outputdir OUTPUT_DIR
#                        Path to output directory
#  -cf CONFIG_FILE_PATH  Name of your configuration file: project_run_config_V1
#  -t TASK [TASK ...]
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
The arguments that you specify really depend on the steps you wan to run. 

The pipeline can process ATACseq, ChIPseq and RNAseq data. You need to specify the technology in the configuration file. If you want to run all tasks, then the pipeline will know which steps to run. 
Each technology has its own specific steps. 

ATACseq: 1, 2, 3, 4, 4.1, 5, 6, 7, 8
ChIPseq: 1, 2, 3, 4, 5, 6, 7, 8
RNAseq: 2,4,9



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
