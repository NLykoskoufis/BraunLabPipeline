#!/usr/bin/env Rscript 

args = commandArgs(trailingOnly=TRUE)

library(ATACseqQC)

INPUT <- args[1]
OUTDIR <- args[2]


bamfile.label <- sapply(strsplit(basename(INPUT), "\\."),"[[",1)
output_pdf <- paste0(OUTDIR, "/",bamfile.label,"_fragSizeDistPlot.pdf")
output_png <- paste0(OUTDIR, "/",bamfile.label,"_fragSizeDistPlot.png")

#pdf(output_pdf,height=5,width=6)
#fragSizeDist(INPUT, bamfile.label)
#dev.off()
png(output_png, height=600,width=800)
fragSizeDist(INPUT, bamfile.label)
dev.off()


