#!/usr/bin/env python3 

from os import read, sep
import os.path
import sys 
from collections import defaultdict 
import re
import gzip 
import argparse
import pandas as pd 
# ===========================================================================================================


DESC_COMMENT = "Combine all samtools stats together"
SCRIPT_NAME = "createSamtoolsStatsTable.py"
# ===========================================================================================================

"""
#===============================================================================
@author: Nikolaos Lykoskoufis
@date: 4th November 2021
@copyright: Copyright 2021, University of Geneva
Combine all samtools stats together
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



def readStats(fstats): 
    dico = defaultdict(dict) 
    for file in fstats: 
        print(f"  * Reading [{file}]")
        sample = os.path.basename(file).replace("_bamStats","")
        f = Utils.myopen(file)
        for line in (line.rstrip().split("\t") for line in f):
            if line[0] == "SN":
                dico[sample][line[1].replace(":","")] = line[2]
            elif line[0] == "FFQ": 
                break
            else:
                continue
    return dico 


def dicoTOcsv(dico, fcsv):
    df = pd.DataFrame.from_dict(dico,orient='index')
    df['samples'] = df.index
    cols = df.columns.tolist()
    cols = cols[-1:] + cols[:-1]
    df = df[cols]
    df.to_csv(fcsv, index=False)


parser = argparse.ArgumentParser(description='Combine samtools Stats together into csv file')
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
    print("  * Generating dictionary")
    dico = readStats(args.ftxts)
    print("  * Generating data frame and saving to csv file")
    dicoTOcsv(dico, args.outputFile)
    
