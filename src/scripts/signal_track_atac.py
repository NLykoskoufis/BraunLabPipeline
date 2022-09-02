#!/usr/bin/env python3 

# BRAUNLP MACS2 signal pvalue bigwig creation
# Check https://github.com/ENCODE-DCC/atac-seq-pipeline/blob/master/src/encode_task_macs2_signal_track_atac.py as the following code is inspired from the ENCODE atac-seq pipeline


import sys 
import os
import subprocess
import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(prog='signal p-value BigWig file creation',
                                     description='')
    parser.add_argument('--bam', type=str, dest = "bam",
                        help='Path to BAM file for TAG counting')
    parser.add_argument('--prefix', type=str, dest = "prefix",
                        help="Prefix name")
    parser.add_argument('--input-path', type=str, dest = "inputDir",
                        help="Path to bedgraph files")
    parser.add_argument('--chrsz', type=str, dest = "chromSizes",
                        help='2-col chromosome sizes file.')
    parser.add_argument('--out-dir', default='', type=str, dest = "outputDir",
                        help='Output directory.')
    parser.add_argument('-@',"--threads",type=int, dest = "threads",
                        help="number of threads")
    parser.add_argument('-macs2',"--macs2-path", type=str, default = "macs2", dest = "macs2Path",
                        help="specify specific macs2 path otherwhise looks in path")
    parser.add_argument('-bedt',"--bedtools-path", type=str, default = "bedtools", dest = "bedtoolsPath",
                        help="specify specific bedtools path otherwhise looks in path")
    parser.add_argument("-bg2bw", '--bg2bw-path', type=str, default = "bedGraphToBigWig", dest = "bg2bwPath",
                        help="specify specific bedtools path otherwhise looks in path")
    parser.add_argument("--bedClip", type=str, default = "bedClip", dest = "bedClipPath",
                        help="specify specific bedClip path otherwhise looks in path")
    args = parser.parse_args()

    return args


def getTAGcount(bam,threads):
    cmd = "/srv/beegfs/scratch/shares/brauns_lab/Tools/samtools-1.12/samtools flagstat {} -@ {} | grep 'properly paired' | cut -d\" \" -f1".format(bam,threads)
    return float(subprocess.check_output(cmd,shell=True, universal_newlines= True, stderr=subprocess.STDOUT).rstrip()) / 1000000.0

def macs2_signal_track(inputDirectory, samplePrefix, chromSizes, sval,outputDirectory,macs2Path, bedtoolsPath, bg2bwPath, bedClipPath):
    # Define output file names 
    pval_bigwig = "{}/{}.pval.signal.bigwig".format(outputDirectory, samplePrefix)
    pval_bedgraph = "{}/{}.pval.signal.bedgraph".format(outputDirectory, samplePrefix)
    pval_bedgraph_srt = "{}/{}.pval.signal.srt.bedgraph".format(outputDirectory, samplePrefix)
    
    ppois_cmd = "{bin} bdgcmp -t {inputDir}/{prefix}_treat_pileup.bdg -c {inputDir}/{prefix}_control_lambda.bdg --o-prefix {prefix} --outdir {outDir} -m ppois -S {sval}".format(bin = macs2Path, inputDir = inputDirectory, prefix = samplePrefix, outDir = outputDirectory, sval = sval)
    
    slopClip_cmd = "{bedtools} slop -i {dir}/{prefix}_ppois.bdg -g {chromSize} -b 0 | {bedclip} stdin {chromSize} {outputFile}".format(bedtools = bedtoolsPath, dir = outputDirectory, prefix = samplePrefix, chromSize = chromSizes, outputFile = pval_bedgraph, bedclip = bedClipPath)
    
    sort_cmd = "LC_COLLATE=C sort -k1,1 -k2,2n {pval_bedgraph} | awk 'BEGIN{{OFS=\"\\t\"}}{{if (NR==1 || NR>1 && (prev_chr!=$1 || prev_chr==$1 && prev_chr_e<=$2)) {{print $0}}; prev_chr=$1; prev_chr_e=$3;}}' > {pval_bedgraph_srt}".format(pval_bedgraph = pval_bedgraph, pval_bedgraph_srt = pval_bedgraph_srt)
    
    bg2bw_cmd = "{bin} {pval_bedgraph_srt} {chromSizes} {pval_bigwig}".format(bin = bg2bwPath, pval_bedgraph_srt = pval_bedgraph_srt, chromSizes = chromSizes, pval_bigwig = pval_bigwig)
    
    # run ppois_cmd
    print("running ppois cmd")
    print(ppois_cmd)
    subprocess.run(ppois_cmd, shell = True, universal_newlines= True, stderr=subprocess.STDOUT)
    
    # run slopClip_cmd 
    print("running slopCLip_cmd")
    print(slopClip_cmd)
    subprocess.run(slopClip_cmd, shell = True, universal_newlines= True, stderr=subprocess.STDOUT)
    
    # run sort_cmd 
    print("running sorting")
    print(sort_cmd)
    subprocess.run(sort_cmd, shell = True, universal_newlines= True, stderr=subprocess.STDOUT)
    
    # run bg2bw_cmd 
    print("running bg2bw_cmd")
    print(bg2bw_cmd)
    subprocess.run(bg2bw_cmd, shell = True, universal_newlines= True, stderr=subprocess.STDOUT)
    
    # remove temporary files 
    
    

def main(): 
    # read parameters 
    args = parse_arguments()
    
    # get Sval 
    print("running getTAGcount")
    sval = getTAGcount(args.bam, args.threads)
    #sval = 0.0
    print(f"sval={str(sval)}")
    # generate bigwig file 
    macs2_signal_track(args.inputDir, args.prefix, args.chromSizes, sval, args.outputDir, args.macs2Path, args.bedtoolsPath, args.bg2bwPath, args.bedClipPath)
    
    print("All Done")
    
if __name__ == "__main__":
    main()
    