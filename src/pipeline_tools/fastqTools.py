#!/usr/bin/env python3 

import glob
import os.path
import re 

def getFastqPrefix(fastq_path): 
    #regex = "_R[12]_*.fastq.gz"
    FILES = glob.glob(f"{fastq_path}/*fastq.gz")
    FILES = set([re.sub("_R[12]_.*.fastq.gz","",os.path.basename(i)) for i in FILES])
    return list(FILES)