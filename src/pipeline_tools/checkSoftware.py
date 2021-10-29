#!/usr/bin/env python3 
import subprocess 
import re 
from pathlib import Path

FAIL=re.compile('''command not found''')

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

def checkSoftware(software):
    cmd = f"{software} --help"
    try:
        subprocess.check_output(cmd, shell=True, universal_newlines=True,stderr=subprocess.STDOUT)
        print(f"{software} {bcolors.OKGREEN}{bcolors.BOLD}installed{bcolors.ENDC}")
        return True
    except subprocess.CalledProcessError as e:
        if FAIL.search(e.output):
            print(f"{software} {bcolors.FAIL}not installed or not correct directory{bcolors.ENDC}")
            return False
        else:
            print(f"{software} {bcolors.OKGREEN}{bcolors.BOLD}installed{bcolors.ENDC}")
            return True

print(" * Trying to load specific modules needed by the pipeline.")

try: 
    import rich 
    print(f" * [rich] module {bcolors.OKGREEN}{bcolors.BOLD}installed{bcolors.ENDC}")
except ModuleNotFoundError:
    print(f"{bcolors.FAIL}rich module not installed. INSTALLING...{bcolors.ENDC}")
    subprocess.check_output("pip3 install rich --user",shell=True,universal_newlines=True,stderr=subprocess.STDOUT)
    
try: 
    import markdown
    print(f" * [markdown] module {bcolors.OKGREEN}{bcolors.BOLD}installed{bcolors.ENDC}")
except ModuleNotFoundError:
    print(f"{bcolors.FAIL}markdown module not installed. INSTALLING...{bcolors.ENDC}")
    subprocess.check_output("pip3 install markdown --user",shell=True,universal_newlines=True,stderr=subprocess.STDOUT)

try: 
    import mdtable
    print(f" * [mdtable] module {bcolors.OKGREEN}{bcolors.BOLD}installed{bcolors.ENDC}")
except ModuleNotFoundError:
    print(f"{bcolors.FAIL}mdtable module not installed. INSTALLING...{bcolors.ENDC}")
    subprocess.check_output("pip3 install mdtable --user",shell=True,universal_newlines=True,stderr=subprocess.STDOUT)

print("\n * Checking whether required software by the pipeline can be accessed\n")



#cutadat 
cutadapt=f"{str(Path.home())}/.local/bin/cutadapt"
if not checkSoftware(cutadapt):
    print("cutadapt not install locally. Attempting to install it")
    subprocess.check_output("pip3 install cutadapt --user",shell=True,universal_newlines=True,stderr=subprocess.STDOUT)
    if checkSoftware(cutadapt): 
        print("cutadapt insatlled locally and ready to go!")
    else:
        print("There is still a problem. Check manually. Nothing more that I can do")
else: 
    print("cutadapt is properly installed and ready to go")
    
#multiqc
multiqc=f"{str(Path.home())}/.local/bin/multiqc"
if not checkSoftware(multiqc):
    print("multiqc not install locally. Attempting to install it")
    subprocess.check_output("pip3 install multiqc --user",shell=True,universal_newlines=True,stderr=subprocess.STDOUT)
    if checkSoftware(cutadapt): 
        print("multiqc insatlled locally and ready to go!")
    else:
        print("There is still a problem. Check manually. Nothing more that I can do")
else: 
    print("multiqc is properly installed and ready to go")



#FastQC
FastQC="/srv/beegfs/scratch/shares/brauns_lab/Tools/FastQC/fastqc"
checkSoftware(FastQC)

#multiQC
multiQC="/srv/beegfs/scratch/shares/brauns_lab/Tools/multiqc/bin/multiqc"
checkSoftware(multiQC)

#Path to cutadapt
cutadapt="/srv/beegfs/scratch/shares/brauns_lab/Tools/cutadapt/bin/cutadapt"
checkSoftware(cutadapt)

#Bedtools 
bedtools="/srv/beegfs/scratch/shares/brauns_lab/Tools/bedtools2/bin/bedtools"
checkSoftware(bedtools)

#Path to bowtie2
bowtie2="/srv/beegfs/scratch/shares/brauns_lab/Tools/bowtie2-2.4.4/bowtie2"
checkSoftware(bowtie2)

#Path to STAR
star="/srv/beegfs/scratch/shares/brauns_lab/Tools/STAR-2.7.5c/bin/Linux_x86_64_static/STAR"
checkSoftware(star)

#Path to samtools
samtools="/srv/beegfs/scratch/shares/brauns_lab/Tools/samtools-1.12/samtools"
checkSoftware(samtools)

#QTLtools
QTLtools="/srv/beegfs/scratch/shares/brauns_lab/Tools/qtltools/bin/QTLtools"
checkSoftware(QTLtools)

#PICARD-Tools
picard="java -Xmx8g -jar /srv/beegfs/scratch/groups/funpopgen/bin/picard.jar"
checkSoftware(picard)

#WSBATCH
wsbatch="/srv/beegfs/scratch/groups/funpopgen/bin/wsbatch"
checkSoftware(wsbatch)

#bamCoverage, 
bamCoverage="/srv/beegfs/scratch/shares/brauns_lab/bin/bamCoverage"
checkSoftware(bamCoverage)

#MACS2
macs2="/srv/beegfs/scratch/shares/brauns_lab/Tools/MACS2-2.2.7.1/bin/macs2"
checkSoftware(macs2)

#bedClip
bedClip="/srv/beegfs/scratch/shares/brauns_lab/bin/bedClip"
checkSoftware(bedClip)

plotBam="/srv/beegfs/scratch/shares/brauns_lab/Tools/samtools-1.12/misc/plot-bamstats"
checkSoftware(plotBam)

print(f"\n * {bcolors.OKGREEN}{bcolors.BOLD}Done :){bcolors.ENDC}")

