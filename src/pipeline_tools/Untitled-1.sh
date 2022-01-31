/srv/beegfs/scratch/shares/brauns_lab/bin/wsbatch  --time=12:00:00 --mem=40G --partition=shared-cpu -n 1 -N 1 -c 8 -o /srv/beegfs/scratch/shares/brauns_lab/data/nikos/BAFinhibitor/data_raw/rnaseq/test/bam/log/08fe29f2_slurm-%j.out --wrap="/srv/beegfs/scratch/shares/brauns_lab/Tools/STAR-2.7.5c/bin/Linux_x86_64_static/STAR --outFilterMultimapNmax 20 --alignSJoverhangMin 8 --alignSJDBoverhangMin 1 --outFilterMismatchNmax 999 --outFilterMismatchNoverLmax 0.6 --alignIntronMin 20 --alignIntronMax 1000000 --alignMatesGapMax 1000000 --outFileNamePrefix /srv/beegfs/scratch/shares/brauns_lab/data/nikos/BAFinhibitor/data_raw/rnaseq/test/bam/13ESConR1.trim. --genomeDir /srv/beegfs/scratch/shares/brauns_lab/data/indexes/STAR/GRCm38_gencode.M10_55bp-readLength --readFilesIn /srv/beegfs/scratch/shares/brauns_lab/data/nikos/BAFinhibitor/data_raw/rnaseq/test/trimmed_fastq/13ESConR1.trim*_R1_001.fastq.gz; /srv/beegfs/scratch/shares/brauns_lab/Tools/samtools-1.12/samtools sort/srv/beegfs/scratch/shares/brauns_lab/data/nikos/BAFinhibitor/data_raw/rnaseq/test/bam/13ESConR1.trim.Aligned.out.sam -O BAM -o /srv/beegfs/scratch/shares/brauns_lab/data/nikos/BAFinhibitor/data_raw/rnaseq/test/bam/13ESConR1.trim.Aligned.sortedByCoord.out.bam; /srv/beegfs/scratch/shares/brauns_lab/Tools/samtools-1.12/samtools index /srv/beegfs/scratch/shares/brauns_lab/data/nikos/BAFinhibitor/data_raw/rnaseq/test/bam/13ESConR1.trim.Aligned.sortedByCoord.out.bam"