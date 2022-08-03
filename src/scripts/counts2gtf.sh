#!/bin/bash

COUNTS=$1
OUTPUT=$2

awk '{print $1"\tpeaks\texon\t"$2+1"\t"$3"\t.\t+\t.\tgene_id \""$1"_"$2"_"$3"\"; gene_name \""$1"_"$2"_"$3"\";"}' ${COUNTS} > ${OUTPUT}