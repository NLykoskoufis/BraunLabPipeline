#!/usr/bin/env Rscript 

args = commandArgs(trailingOnly=TRUE)

library(ATACseqQC)

INPUT <- args[1]
OUTDIR <- args[2]


bamfile.label <- sapply(strsplit(basename(INPUT), "\\."),"[[",1)
output <- paste0(OUTDIR, "/",bamfile.label,"_fragSizeDistPlot.pdf")
pdf(output,height=5,width=6)
fragSizeDist(bamfile, bamfile.label)
dev.off()


