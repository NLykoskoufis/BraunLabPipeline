#!/bin/bash 

BIN=$1 
BAM=$2
BED=$3

${BIN} bamtobed -i ${BAM} | awk '{print $1"\t"$2"\t"$3"\t"$3-$2"\t"$5"\t"$6}' > ${BED}
