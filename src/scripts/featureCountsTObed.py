#!/usr/bin/env python3 

import sys 
from collections import defaultdict 
import re
import gzip 
import os.path 

# ===========================================================================================================
from typing import DefaultDict


DESC_COMMENT = "Script to transform a featureCounts counts to proper bed file"
SCRIPT_NAME = "countsTObed.py"
# ===========================================================================================================

"""
#===============================================================================
@author: Nikolaos Lykoskoufis
@date: 10th of September 2021
@copyright: Copyright 2020, University of Geneva
Transform featureCounts counts.txt file to proper bed file
#===============================================================================
"""

class Utils:
    def __init__(self):
        pass
    @staticmethod
    def myopen(filename):
        '''Checking to see if file is gzipped or not'''
        f = gzip.open(filename)
        try:
            f.read(2)
            f.close()
            return gzip.open(filename,"rt")
        except:
            f.close()
            return open(filename,"rt")
            
def readAnnotationGTF(fgtf):
    dico = defaultdict(dict)
    f = Utils.myopen(fgtf)
    for line in (re.split('''\t|;| ''',line.rstrip()) for line in f):
        if line[0].startswith("#"):
            continue
        else:
            if line[2] == "gene":
                
                chrom = line[0]
                start = line[3]
                end = line[4]
                strand = line[6]
                geneID = line[9].replace("\"","")
                geneName = line[15].replace('"',"")
                if line[20] == "gene_biotype":
                    geneType = line[21].replace('"',"")
                elif line[11] == "gene_type":
                    geneType = line[12].replace('"',"")
                else: 
                    print("WARNING: Unable to find geneType.")
                TSS = start if strand == "+" else end
                dico[geneID]['chr'] = chrom
                dico[geneID]['start'] = str(start)
                dico[geneID]['end'] = str(end)
                dico[geneID]['strand'] = strand
                dico[geneID]['name'] = geneName
                dico[geneID]['type'] = geneType
                dico[geneID]['tss'] = int(TSS)
    return dico


def TXT2BED(ftxt, fgtf, fout):
    dico = readAnnotationGTF(fgtf)
    f = Utils.myopen(ftxt)
    g = open(fout,"w")
    for line in (line.rstrip().split("\t") for line in f):
        if line[0].startswith("#"):
            pass
        elif line[0] == "Geneid":
            header = line
            g.write("#chr\tstart\tend\tgene\tinfo\tstrand\t"+ "\t".join([os.path.basename(i).split(".")[0] for i in header[6:]])+ "\n")
        else:
            gene = line[0]
            length = str(line[5])
            chrom = dico[gene]['chr']
            tss = dico[gene]['tss']
            info = "L={length};T={type};R={chrom}:{start}-{end};N={name}".format(length = length, type = dico[gene]['type'], chrom = chrom, start = str(dico
[gene]['start']), end = str(dico[gene]['end']), name = dico[gene]['name'])
            g.write(chrom + "\t" + str(tss-1) + "\t" + str(tss) + "\t" + gene + "\t" + info + "\t" + dico[gene]['strand'] + "\t" + "\t".join(line[6:])+ "\n"
)
            
TXT2BED(*sys.argv[1:])