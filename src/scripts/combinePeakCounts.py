#!/usr/bin/env python3 

import os.path
import sys 
from collections import defaultdict 
import re
import gzip 
import argparse
# ===========================================================================================================


DESC_COMMENT = "Script to transform a peakCounts to proper bed file"
SCRIPT_NAME = "combinePeakCounts.py"
# ===========================================================================================================

"""
#===============================================================================
@author: Nikolaos Lykoskoufis
@date: 4th November 2021
@copyright: Copyright 2021, University of Geneva
Script to transform a peakCounts to proper bed file
#===============================================================================
"""

class Utils:
    def __init__(self):
        pass
    @staticmethod
    def myopen(filename):
        """[checks to see whether file is compressed or not]
        Arguments:
            self {[string]} -- [file name]
        Returns:
            [object] -- [IO object]
        """        
        f = gzip.open(filename)
        try:
            f.read(2)
            f.close()
            return gzip.open(filename,"rt")
        except:
            f.close()
            return open(filename,"rt")
            

def combineCounts(fileList, outputbed):
    dico = defaultdict(list)
    for file in fileList:
        print(f"  * Reading [{file}]")
        sample = os.path.basename(file).split(".")[0]
        dico['samples'].append(sample)
        f = Utils.myopen(file)
        linecount = 0 
        for line in (line.rstrip().split("\t") for line in f):
            if linecount % 100000 == 0: print(f"  * Read {linecount} lines")
            linecount += 1
            key = f"{line[0]};{line[1]};{line[2]}"
            dico[key].append(line[3])
    
    print("  * Combining all data into multisample bed file")
    with open(outputbed, "w") as g: 
        g.write("#chr\tstart\tend\tid\tinfo\tstrand\t" + "\t".join(dico['samples']) + "\n")
        dico.pop('samples',None)
        for key, values in dico.items():
            chrom = key.split(";")[0]
            start = int(key.split(";")[1])
            end = int(key.split(";")[2])
            strand = "+" # I add plus as regarding peaks strand does not matter. 
            id = key.replace(";","_")
            info = f"L={end-start};T=ATACpeak;R={chrom}:{start}-{end}" 
            g.write(chrom + "\t" + str(start - 1) + "\t" + str(end) + "\t" + id + "\t" + info + "\t" + strand + "\t" + "\t".join(dico[key]) + "\n")


parser = argparse.ArgumentParser(description='Combine peakCounts files to bed file.')
parser.add_argument('-v', dest='version', action='store_true', help='Display pipeline version')
#If user is asking for version
if len(sys.argv) > 1:
    if sys.argv[1] == '-v':
        print('Pipeline version 1.00\n### BETA VERSION. USE IT WITH CAUTION!!!')
        sys.exit(0)

parser.add_argument('-f', '--file-list', dest='ftxts',required=True, type=str, nargs="+", help='List of files to combine together')
parser.add_argument("-out", '--outputFile', dest='outputFile', required=True, type=str, help = "output file name")

####################
#    CHECK ARGS    #
####################

if __name__ == "__main__":
    #Get command line args
    args = parser.parse_args()
    combineCounts(args.ftxts, args.outputFile)
        
