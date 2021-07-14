#!/bin/bash 

BED=$1
EXTENSION=$2
GENOMESIZEFILE=$3
OUTPUT=$4
BIN="/home/users/l/lykoskou/bin/bedClip"


awk -F '\t' -v ext=${EXTENSION} '{if($6=="+") {print $1,$2,$2+ext,ext,$5,$6} else {print $1,$3-ext,$3,ext,$5,$6}}' ${BED} | LC_COLLATE=C sort -k1,1 -k2,2n > ${OUTPUT}_temp.bed

${BIN} ${OUTPUT}_temp.bed ${GENOMESIZEFILE} ${OUTPUT}

#rm ${OUTPUT}_temp.bed