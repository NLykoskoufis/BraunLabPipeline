#!/bin/bash 

BED=$1
EXTENSION=$2
BIN=""


bedClip ${file}.NoDup.Ext${extension}.temp.bed $genomeSizeFile ${file}.NoDup.Ext${extension}.bed

rm ${file}.NoDup.Ext${extension}.temp.bed