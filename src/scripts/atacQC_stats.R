#!/usr/bin/env Rscript 

args = commandArgs(trailingOnly=TRUE)

library(ATACseqQC)

INPUT <- args[1]
OUTPUT <- args[2]

qc <- bamQC(INPUT,outPath=NULL)

totalQNAMEs = as.numeric(qc$totalQNAMEs)
properPairRate = as.numeric(qc$properPairRate)
unmappedRate = as.numeric(qc$unmappedRate)
notPassingQualityControlsRate = as.numeric(qc$notPassingQualityControlsRate)
NRF = as.numeric(qc$nonRedundantFraction)
PCR_1 = as.numeric(qc$PCRbottleneckCoefficient_1)
PCR_2 = as.numeric(qc$PCRbottleneckCoefficient_2)

df <- data.frame("totalQNAMEs"=totalQNAMEs,
                "properPairRate" = properPairRate,
                "unmappedRate" = unmappedRate,
                "notPassingQualityControlsRate" = notPassingQualityControlsRate,
                "nonRedundantFraction"=NRF,
                "PCR_bottleneck_Coefficient_1" = PCR_1,
                "PCR_bottleneck_Coefficient_2" = PCR_2)

write.table(df, file=OUTPUT, col.names=TRUE, row.names=FALSE,sep=",",quote=FALSE)